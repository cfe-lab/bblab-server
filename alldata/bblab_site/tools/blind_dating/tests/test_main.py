import blind_dating as bd

def test_regress_cmd():
    actual = bd.get_regress_cmd(1, 2, '/some/path')
    expected = ['Rscript', '/alldata/bblab_site/tools/blind_dating/repo/src/root_and_regress.R', '--runid=13615', '--tree=1', '--info=2', '--rootedtree=/some/path/rooted_tree.nwk', '--data=/some/path/data.nwk', '--stats=/some/path/stats.nwk']
    expected[2] = actual[2]
    assert actual == expected