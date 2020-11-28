# Hugo Rotary theme

This is a theme for building websites using [Hugo](gohugo.io) framework. It
is intended to build websites for Rotary clubs: if you need a static website,
one simply has to fill the contents needed.

The website supports multiple languages and depending on the setup and the
contents, they could have different data. This makes it easier to show the
most relevant information in as many languages as possible but also does not
require to translate everything.

The intention of this guide is to make it possible to setup and run a website
even if one lacks deep understanding of Hugo. Bear in mind that still there is
some domaign specific knowledge required.

## How to setup

While contents can vary greatly, the general structure of the project shall
look something like this:

```
.
├── Makefile
├── config.toml
├── content
│   ├── about
│   │   └── history
│   ├── news
│   └── projects
├── public
├── static
│   └── img
│       └── club-picture.jpg
└── themes
    └── gohugo-theme-rotary
```

There is an example Makefile and config.toml in `./example/`. You are expected
to adapt that to your needs.

Your data lives in the `content` dir. It is the home of the markdown and
images for your pages. Those are later on applied to the templates of the
theme. You can have different directories there and those represent the URLs
of your website. For example if you have directory `./content/rotary/` its
contents would be hosted under `baseURL/rotary`. Furthermore, if you have a
subdir in it, ex. `./content/rotary/foundation`, it would be served under
`baseURL/rotary/foundation`. This allows a flexible structure of the website
to match your needs.

Despite this, there are some special directories that are expected by the
theme.

* `content/about/history/` - on the landing page there is a picture and some
  text beneath it. This directory is the holder of the text.

* `content/projects/` - this is where the projects are defined. Each project
  lives in its own subdir.

* `content/news/` - this is where the news go. Each news lives in its own
  subdir

* `public` - this is where the static files for the website are produced. The
  publish script in the `example/Makefile` uploads the contents of this
  directory to the FTP

* `static/img/club-picture.jpg` - this is the image on the landing page

* `themes/gohugo-theme-rotary` - this is where you're expected to clone this
  repo

Each piece of data can be defined in a different language. The language itself
is part of the name of the file and it corresponds to the language code - for
example `en` for English as shown:

```
ls content/about/history/
charter.png	index.bg.md	index.en.md
```

In this example, the `index.en.md` would be shown in the English language
version while the `index.bg.md` would be visible in the Bulgarian one. Note
that there is no German, nor Swedish index files so nothing would be shown in
those language versions of the website. If we want to have such pages, we
shall add the `index.de.md` or `index.se.md` respectively. This allows
building custom-fit experiences for the different languages your website would
support, if any.

### Config

You can find an example config in `/example/config.toml`. It is adapted for
the needs of Rotary Club Sofia Triaditsa. Let's go through it briefly.

```
baseURL = "https://rotarytriaditsa.org/"
enableRobotsTXT = true
DefaultContentLanguage = "bg"
theme = "gohugo-theme-rotary"
```

One shall put the root domaign of their website in `baseURL`.

The generation of `robots.txt` can be disabled from the config. Note that if
enabled, by default a file will be generated that forbids crawlers to index
the website. This is useful in debug and test environments. If you want to use
indexing - you must add `HUGO_ENV=production` to your build command.

`DefaultContentLanguage` sets the default language that is being used when
loading the root of the domaign.

`theme` is Hugo specific setting that defines which theme is to be used. A
site can have multiple themes while only one is being active.

#### Languages

In the section `Languages` one shall define all language versions of the
website. This could as well be a single one. In the example file there are 4
different languages supported: Bulgarian, English, German and Swedish. Each
one of them defines a set of data for the club, especially with the focus of
localization.

```
  [languages.sv]
    title = "Rotary club Sofia Triaditsa"
    weight = 3
    LanguageName = "Svenska"
    [[languages.sv.menu.main]]
        identifier = "Home"
        name = "Hem"
        url = "/sv"
        weight = -110
    [languages.sv.params]
      [languages.sv.params.club]
        name ="Sofia Triaditsa"
        country ="Bulgaria"
        id = "88428"
        district_url = "https://www.rotary-bulgaria.org/"
        location = "Hotel Marinela"
        addressLine1 = "Blvd James Bourchier 100"
        addressLine2 = "1407 Lozenets, Sofia"
        meetingTime = "7 pm, varje måndag"
```

Note that this includes localized version of the club name, meeting place and
time and etc.

This section also defines the website menu (if any). In the example above the
menu has only one entry - home (hem in Swedish). This is not the case with the
English version:

```
  [languages.en]
    title = "Rotary club Sofia Triaditsa"
    weight = 2
    LanguageName = "English"
    [[languages.en.menu.main]]
        identifier = "Home"
        name = "Home"
        url = "/en"
        weight = -110
    [[languages.en.menu.main]]
      identifier = "About"
      name = "About"
      weight = -100
    [[languages.en.menu.main]]
      name = "Contacts"
      url = "/en/about/contact"
      weight = -90
      parent = "About"
    [[languages.en.menu.main]]
      name = "Our story"
      url = "/en/about/history"
      weight = -80
      parent = "About"
    [[languages.en.menu.main]]
      name = "Projects"
      url = "/en/projects"
      weight = -70
      parent = "About"
    [[languages.en.menu.main]]
      name = "Rotary Foundation"
      url = "/en/rotary/foundation"
      weight = -60
    [[languages.en.menu.main]]
      name = "News"
      url = "/en/news/"
      weight = -50
    [languages.en.params]
      [languages.en.params.club]
        name ="Sofia Triaditsa"
        country ="Bulgaria"
        id = "88428"
        district_url = "https://www.rotary-bulgaria.org/"
        location = "Hotel Marinela"
        addressLine1 = "Blvd James Bourchier 100"
        addressLine2 = "1407 Lozenets, Sofia"
        meetingTime = "7 pm, every Monday"
```

Note that here the section with the menu is much more detailed: each entry has
a set of params. They define the menu of the website.
* identifier - a variable name for nested menu elements
* name  - how it is visualised in this language, this is the label of the link
  to the corresponding website section
* url - (optional) the website's url where the menu link would lead to
* weight - a means to order the menu elements: the first one visualised it the
  one with the lowest weight
* parent - (optional) this defines the element as a nested one, the value of
  the parent is the corresponding identifier

It is worth mentioning that the default menu and corresponding params are
taken out of the languages section and is at the end of the config file.

#### Params

Those are a set of global variables for the website. They are pretty obvious
how to use.

```
[params]
  facebook = "your facebook page url"
  [params.tracking]
    googleTag = "your google tag id"
```



### Markdown structure

TODO

## Building and deployment

There is a Makefile in the `example/` dir: it has some general commands to
use:
`make serve` builds and runs the website. You can access it on
`localhost:1313`. Any chagnes being made to the config, templates or contents
would result in rebuilding the site.

`make publish` builds the website with `robots.txt` set to allow
crawlers to index all pages. It also publishes it to the FTP server. Feel free
to adjust it to your needs.
