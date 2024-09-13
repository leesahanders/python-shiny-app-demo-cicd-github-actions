# Using GitHub Actions to Test & Deploy to RStudio Connect

RStudio Connect hosts a variety of data artifacts with different development 
life cycles. Whenever you want to publish one of these data artifacts to RStudio 
Connect, there are three paths you can follow:

 - Push-button deployment process within the RStudio IDE
 - Git-backed deployment within RStudio Connect
 - Programmatic deployment

This repository is an example of the third deployment path using GitHub Actions as
a CI/CD pipeline to test and deploy a Shiny application to RStudio Connect. 

If you want to learn more about it you can read: [https://solutions.rstudio.com/data-science-admin/deploy/ci-cd/github-actions/](https://solutions.rstudio.com/data-science-admin/deploy/ci-cd/github-actions/)

## Usage

Setup the `renv` environment:

```r
renv::activate()
renv::restore()
```

To run the app either open `app/app.R` and click the "Run App" button at the top of the IDE code pane or use:

```r
shiny::runApp("app")
```

## Deployment

### Push Button

Open `app/app.R` and use the blue publish icon in the upper right corner of the IDE code pane.

### rsconnect package

You can also deploy using the rsconnect package:

```
rsconnect::deployApp(
  appDir = "app",
  appTitle = "Shiny Penguins"
)
```

### Git-backed

Update the code, and then run:

```r
rsconnect::writeManifest("app")
```

Commit the new `manifest.json` file to the git repo along with the code.

## Resources

[Posit Connect User Guide: Shiny](https://docs.posit.co/connect/user/shiny/)

