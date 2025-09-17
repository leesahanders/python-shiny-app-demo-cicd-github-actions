# Using GitHub Actions to Test & Deploy to RStudio Connect

RStudio Connect hosts a variety of data artifacts with different development 
life cycles. Whenever you want to publish one of these data artifacts to RStudio 
Connect, there are three paths you can follow:

 - Push-button deployment process within the RStudio IDE
 - Git-backed deployment within RStudio Connect
 - Programmatic deployment

This repository is an example of the third deployment path using GitHub Actions as
a CI/CD pipeline to test and deploy a Shiny application to RStudio Connect. 

If you want to learn more about it you can read: [https://solutions.rstudio.com/data-science-admin/deploy/ci-cd/github-actions/](https://solutions.rstudio.com/data-science-admin/deploy/ci-cd/github-actions/) and the [various supported actions here](https://github.com/rstudio/actions)

## Usage

### uv 

In that example I created my uv venv with the below, after making sure that I was "cd'd" to the correct directory:

```bash
# Check what python versions you have access to
ls -1d /opt/python/*

# Create the uv project, this example declares the python version to use explicitly. Make sure this matches a version you have access to.
uv init --app --python 3.12.11

# Create a virtual environment 
uv venv

# Initialize the venv 
source .venv/bin/activate

# Install needed packages
uv pip install shiny
```

If using a specific version of a package make sure it is called out both in the python-versions file and the pyproject.toml file like this:

```
dependencies = [
    "databricks-connect==14.3.3",
]
```

After changing anything be sure to run `uv sync`. 

Create a requirements.txt file (for playwright) with: `uv export --format requirements-txt`. 

### venv

Setup the `venv` environment:

```bash
python -m venv .venv
. .venv/bin/activate
# .venv\Scripts\activate # Windows
```

Upgrade pip and then install needed packages:

```bash
pip install --upgrade pip
python -m pip install --upgrade pip wheel setuptools rsconnect-python
pip install -r requirements.txt
```

Run the application:

```bash
shiny run --reload app.py
```

Or run the app with Python: 

```bash
python app.py
```

Leave a virtual environment with:

```bash
deactivate
```

## Run it 

### The uv way

Use [uv](https://github.com/astral-sh/uv). It will detect that this is a project and create the venv for us when we go to run the application. 

Run the application:

```bash
uv run app.py
```

Stuck on the `loading...` screen? Try closing the session and re-running the above command. It seems like there can be a transient issue that happens when the environment setup and app run steps are run together. 

### The pip way

Run the application (after setting up the venv):

```bash
python app.py
```

## Deploy manually

### rsconnect-python CLI

```bash
# With uv
uv run rsconnect deploy shiny .

# Without uv
rsconnect deploy shiny .
```

### Git-backed

Update the code, and then run:

```bash
# With uv
uv export -o requirements.txt --no-hashes
uv run rsconnect write-manifest shiny --overwrite .

# Without uv
pip freeze > requirements.txt 
rsconnect write-manifest shiny --overwrite .
```

## Testing 

Refer to the documentation: <https://shiny.posit.co/py/docs/end-to-end-testing.html#add-tests-an-existing-app> and <https://playwright.dev/python/docs/test-runners> 

Install the requirements: 

```bash
pip install pytest pytest-playwright
playwright install
```

Add tests with: 

```bash
shiny add test
```

pytest conventions for naming the test file are that it should start with `test_`. 

For app.py and test_basic_app.py files in the same directory run: 

```bash
pytest
```

For example the test might be: 

```{.python filename="test_app.py"}
from playwright.sync_api import Page

from shiny.playwright import controller
from shiny.pytest import create_app_fixture
from shiny.run import ShinyAppProc

import pytest

#app = create_app_fixture("..\app.py") # for Linux/Mac
app = create_app_fixture("../app.py") # For Windows

def test_app(page: Page, app: ShinyAppProc):
    page.goto(app.url)
    # Add test code here
    txt = controller.OutputText(page, "txt")
    slider = controller.InputSlider(page, "n")
    slider.set("55")
    txt.expect_value("n*2 is 110")
```

For the app: 

```{.python filename="app.py"}
from shiny import render, ui
from shiny.express import input

ui.panel_title("Hello Shiny!")
ui.input_slider("n", "N", 0, 100, 20)

@render.text
def txt():
    return f"n*2 is {input.n() * 2}"
```


Or another example: 

```{.python filename="test_app.py"}
from app import filter_penguins

def test_filter_penguins():
    assert filter_penguins(["Adelie"]).shape[0] == 152
    assert filter_penguins(["Gentoo"]).shape[0] == 124
    assert filter_penguins(["Chinstrap"]).shape[0] == 68
    assert filter_penguins(["Adelie", "Gentoo"]).shape[0] == 276
    assert filter_penguins(["Adelie", "Gentoo", "Chinstrap"]).shape[0] == 344
```

For the app: 

```{.python filename="app.py"}
from palmerpenguins import load_penguins
from shiny.express import input, render, ui

penguins = load_penguins()

ui.input_select(
  "species", "Enter a species",
  list(penguins.species.unique())
)

@render.data_frame
def display_dat():
    return filter_penguins(input.species())

def filter_penguins(species):
    return penguins[penguins.species.isin(species)]
```

## Updates to CI/CD github action 

If you wanted to add an error:

```
echo "::error file=app.js,line=1::This is a test, ignore"
```

For other parameters that can be changed with the runtime refer to the Connect API: <https://docs.posit.co/connect/api/#patch-/v1/content/-guid-> 

## Updates

Create the requirements file:

```bash
python -m pip freeze > requirements.txt
```

```bash
rsconnect write-manifest shiny .
```

If you are running into deploy issues where there are breaking packages you can edit the requirements file explicitly: 

```bash
# requirements.txt generated by rsconnect-python on 2022-09-21 14:59:58.865441
streamlit==1.11.0
```

To use a Package Manager repository with a specific project defined by a `requirements.txt` file, add `-i [repositoryURL]` to the top of your file, for example:

```bash
-i https://packagemanager.posit.co/pypi/latest/simple
pandas
scipy
```

How to configure a pypi repository globally (using pip.conf): 
<https://docs.posit.co/resources/install-python/#optional-configure-a-pypi-repository>

## Getting the GUID 

```
          CONTENT_NAME="python-shiny-app-demo-cicd-github-actions"
          API_KEY="T0BIFNvRyz9jCtiezw0QU4WMkP1KRTHk"
          CONNECT_SERVER="https://pub.current.posit.team/"
          echo ${{ secrets.CONNECT_SERVER }}/_api__/v1/content?name=${CONTENT_NAME}
          # this works
          curl --silent --show-error -L --max-redirs 0 --fail \
            -X GET \
            -H "Authorization: Key ${API_KEY}" \
            "https://pub.current.posit.team/__api__/v1/content"
          # this works
          curl --silent --show-error -L --max-redirs 0 --fail \
            -X GET \
            -H "Authorization: Key ${API_KEY}" \
            "${CONNECT_SERVER}__api__/v1/content"
          # this works
          curl --silent --show-error -L --max-redirs 0 --fail \
            -X GET \
            -H "Authorization: Key ${API_KEY}" \
            "${CONNECT_SERVER}__api__/v1/content?name=${CONTENT_NAME}"
          echo "Content GUID: $CONTENT_GUID"
          echo  "${{ secrets.CONNECT_SERVER }}
          DATA='{"title": "Python CICD with pytest and Playwright using Github actions"}'
          curl --silent --show-error -L --max-redirs 0 --fail \
            -X PATCH \
            -H "Authorization: Key ${{ secrets.CONNECT_API_KEY }}" \
            --data-raw "${DATA}" \
            "${{ secrets.CONNECT_SERVER }}/__api__/v1/content/${CONTENT_GUID}"
```

## Troubleshooting

### Issues with Python not being on path

Set it manually to an installed Python version with: 

```bash
alias python="/opt/python/3.9.17/bin/python"
```

Set it in your .bashrc on mac or linux so that it is set for your profile every time you log in (typically this is located in the root directory of your home folder): 

```bash
# add this to your .bashrc
export PATH=/opt/python/3.11.9/bin:$PATH
```

Check for the available python versions (if typically installed): 

```bash
ls -ld /opt/python/*
```

## Resources

[Posit Connect User Guide: Shiny for Python](https://docs.posit.co/connect/user/shiny-python/)
