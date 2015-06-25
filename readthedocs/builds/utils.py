import re
import logging
from shutil import rmtree

from builds.constants import LATEST


log = logging.getLogger(__name__)


GH_REGEXS = [
    re.compile('github.com/(.+)/(.+)(?:\.git){1}'),
    re.compile('github.com/(.+)/(.+)'),
    re.compile('github.com:(.+)/(.+).git'),
]

BB_REGEXS = [
    re.compile('bitbucket.org/(.+)/(.+)/'),
    re.compile('bitbucket.org/(.+)/(.+)'),
    re.compile('bitbucket.org:(.+)/(.+)\.git'),
]


def get_github_username_repo(version, repo_url=None):
    if not repo_url:
        repo_url = version.project.repo
    if 'github' in repo_url:
        for regex in GH_REGEXS:
            match = regex.search(repo_url)
            if match:
                return match.groups()
    return (None, None)


def get_bitbucket_username_repo(version, repo_url=None):
    if not repo_url:
        repo_url = version.project.repo
    if 'bitbucket' in repo_url:
        for regex in BB_REGEXS:
            match = regex.search(repo_url)
            if match:
                return match.groups()
    return (None, None)


def get_vcs_version_slug(version):
    if version.slug == LATEST:
        if version.project.default_branch:
            return version.project.default_branch
        else:
            return version.project.vcs_repo().fallback_branch
    return version.commit_name


def get_conf_py_path(version):
    conf_py_path = version.project.conf_file(version.slug)
    conf_py_path = conf_py_path.replace(
        version.project.checkout_path(version.slug), '')
    return conf_py_path.replace('conf.py', '')


def clean_build_path(version):
    '''Clean build path for project version

    Ensure build path is clean for project version. Used to ensure stale build
    checkouts for each project version are removed.

    version
        Instance of :py:class:`readthedocs.builds.models.Version` to perform
        build path cleanup on
    '''
    try:
        path = version.get_build_path()
        if path is not None:
            log.debug('Removing build path {0} for {1}'.format(
                path, version))
            rmtree(path)
    except OSError:
        log.error('Build path cleanup failed', exc_info=True)
