from playwright.sync_api import Page
from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc
import pytest

#app = create_app_fixture("..\app.py") # for Linux/Mac
#app = create_app_fixture("../app.py") # For Windows
app = create_app_fixture("..//app.py") # For CI

def test_app(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    # Add test code here
    txt = controller.OutputText(page, "txt")
    slider = controller.InputSlider(page, "n")
    slider.set("55")
    txt.expect_value("n*2 is 110")

