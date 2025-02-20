from mvt.android.artifacts.artifact import AndroidArtifact
from mvt.android.artifacts.getprop import GetProp
from mvt.android.artifacts.processes import Processes
from mvt.android.artifacts.dumpsys_packages import DumpsysPackagesArtifact
from mvt.android.artifacts.dumpsys_package_activities import (
    DumpsysPackageActivitiesArtifact,
)
from mvt.android.artifacts.dumpsys_appops import DumpsysAppopsArtifact

import os
import logging


def get_artifact_folder():
    return os.path.join(os.path.dirname(__file__), "android")


def get_artifact(fname):
    fpath = os.path.join(get_artifact_folder(), fname)
    if os.path.isfile(fpath):
        return fpath
    return


class TestAndroidArtifact:
    def test_extract_dumpsys_section(self):
        file = get_artifact("dumpsys.txt")
        with open(file) as f:
            data = f.read()

        section = AndroidArtifact.extract_dumpsys_section(
            data, "DUMP OF SERVICE package:"
        )
        assert isinstance(section, str)
        assert len(section) == 3907

    def test_parsing_get_prop(self):
        gp = GetProp()
        file = get_artifact("getprop.txt")
        with open(file) as f:
            data = f.read()

        assert len(gp.results) == 0
        gp.parse(data)
        assert len(gp.results) == 13
        assert gp.results[0]["name"] == "af.fast_track_multiplier"
        assert gp.results[0]["value"] == "1"

    def test_parsing_processes(self):
        p = Processes()
        file = get_artifact("ps.txt")
        with open(file) as f:
            data = f.read()

        assert len(p.results) == 0
        p.parse(data)
        assert len(p.results) == 15
        assert p.results[0]["proc_name"] == "init"

    def test_parsing_dumpsys_packages(self):
        dpa = DumpsysPackagesArtifact()
        file = get_artifact("dumpsys_packages.txt")
        with open(file) as f:
            data = f.read()

        assert len(dpa.results) == 0
        dpa.parse(data)
        assert len(dpa.results) == 2
        assert (
            dpa.results[0]["package_name"]
            == "com.samsung.android.provider.filterprovider"
        )
        assert dpa.results[0]["version_name"] == "5.0.07"

    def test_parsing_dumpsys_package_activities(self):
        dpa = DumpsysPackageActivitiesArtifact()
        file = get_artifact("dumpsys_packages.txt")
        with open(file) as f:
            data = f.read()

        assert len(dpa.results) == 0
        dpa.parse(data)
        assert len(dpa.results) == 4
        assert dpa.results[0]["package_name"] == "com.samsung.android.app.social"
        assert (
            dpa.results[0]["activity"]
            == "com.samsung.android.app.social/.feed.FeedsActivity"
        )

    def test_parsing_dumpsys_appops(self):
        da = DumpsysAppopsArtifact()
        da.log = logging
        file = get_artifact("dumpsys_appops.txt")
        with open(file) as f:
            data = f.read()

        assert len(da.results) == 0
        da.parse(data)
        assert len(da.results) == 13
        assert da.results[0]["package_name"] == "com.android.phone"
        assert da.results[0]["uid"] == "0"
        assert len(da.results[0]["permissions"]) == 1
        assert da.results[0]["permissions"][0]["name"] == "MANAGE_IPSEC_TUNNELS"
        assert da.results[0]["permissions"][0]["access"] == "allow"
        assert da.results[6]["package_name"] == "com.sec.factory.camera"
        assert len(da.results[6]["permissions"][1]["entries"]) == 1
        assert len(da.results[11]["permissions"]) == 4
