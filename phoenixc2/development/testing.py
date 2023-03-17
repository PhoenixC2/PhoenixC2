import os


def change_to_testing_config():
    os.environ["PHOENIX_CONFIG"] = "testing"
    os.environ["PHOENIX_TEST"] = "true"
    os.environ["PHOENIX_PRINT"] = "false"
