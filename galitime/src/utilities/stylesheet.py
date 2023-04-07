#!/bin/env python3
# coding:utf-8
# encoding:utf-8

"""
Module defining custom stylesheets
"""

styles = {
    "COMMON": "",
    "BLUE": "background-color: rgb(50, 50, 200); color: white;",
    "RED": "background-color: rgb(200, 100, 100);",
    "GREEN": "background-color: rgb(100, 200, 100);",
    "DISABLED": "background-color: rgb(200, 200, 200);",
    "TALL": "height: 50px; font-size: 20px;",
    "LARGE": "width: 300px; font-size: 20px;",
    "BIG": "height: 50px; width: 300px; font-size: 20px;",
}


def cssify(rawStyleString: str) -> str:
    """
    cssify : Translates descriptive keywords to CSS-rules compatible with QtWdigets

    Args:
        rawStyleString (str): String containing keywords

    Returns:
        str: CSS string with according rules
    """
    resultCssString = styles["COMMON"]

    for style, css in styles.items():
        if style in rawStyleString.upper():
            resultCssString += css

    return resultCssString
