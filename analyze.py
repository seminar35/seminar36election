#! /usr/bin/env python3

from numpy import string_
import pandas as pd
import json


def parse(file_path, save=True):
    df = pd.read_excel(file_path)

    json_data = {"candidates": []}

    votes = df.loc[df["انتخاب"] != "هنوز پاسخ نداده‌اند"]

    for candidate, vote in votes["انتخاب"].value_counts().iteritems():
        voters_info = votes.loc[votes["انتخاب"] == candidate]
        names = voters_info["نام"].values
        families = voters_info["نام خانوادگی"].values
        voters = map(
            lambda fullname: {"firstname": fullname[0], "lastname": fullname[1]},
            zip(names, families),
        )
        json_data["candidates"].append(
            {
                "name": candidate,
                "vote": vote,
                # "voters": list(voters)
            }
        )

    # write into file
    if save:
        stringify = json.dumps(json_data)
        with open("data.json", "w") as file:
            file.write(stringify)

    return json_data


if __name__ == "__main__":
    print(parse("data.xlsx"))
