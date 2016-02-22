# System imports
import os
from os.path import join

# 3rd party libs
from nose.tools import *
from git import *

# PyGitup imports
from PyGitUp.git_wrapper import GitError, StashError
from tests import basepath, write_file, init_master, testfile_name

test_name = 'stash_error'
repo_path = join(basepath, test_name + os.sep)


def setup():
    master_path, master = init_master(test_name)

    # Prepare master repo
    master.git.checkout(b=test_name)

    # Clone to test repo
    path = join(basepath, test_name)

    master.clone(path, b=test_name)
    repo = Repo(path, odbt=GitCmdObjectDB)
    testfile_path = join(path, testfile_name)

    assert repo.working_dir == path

    # Modify file in master
    master_path_file = join(master_path, testfile_name)
    write_file(master_path_file, 'contents1')
    master.index.add([master_path_file])
    master.index.commit(test_name)

    # Create unmerged paths in working dir
    branch_master = repo.active_branch
    branch_changed = repo.create_head(test_name + '.branch')
    branch_changed.set_commit('HEAD')
    branch_changed.checkout()
    write_file(testfile_path, 'contents1')
    repo.index.add([testfile_path])
    repo.index.commit('Update in branch')

    branch_master.checkout()
    write_file(testfile_path, 'contents2')
    repo.index.add([testfile_path])
    repo.index.commit('Update in origin')

    try:
        repo.git.merge(test_name + '.branch')
    except GitCommandError:
        pass


@raises(StashError)
def test_stash_error():
    """ Run 'git up' with an error while stashing """
    os.chdir(repo_path)

    from PyGitUp.gitup import GitUp
    gitup = GitUp(testing=True)
    gitup.run()