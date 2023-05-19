TVTropes 2.0 Demo
=================

Inspired by the currently non-progressing [TVTropes 2.0 project](https://tvtropes.org/pmwiki/pmwiki.php/Administrivia/TwoPointZero) ([forum thread](https://tvtropes.org/pmwiki/posts.php?discussion=14478420050A97600200)).

# Running

Either create `settings.py` according to the instructions at the top of `importer.py`, or comment out the `initialImport()` call in `main.py` to only use the test pages.

Then run
```
python main.py
```

And open `localhost:8000` in your browser.

# Features
* Modular pages: this is the main point of 2.0. A page is made up of blocks, including page-level blocks (quote, image, description, stinger) and examples. Blocks can be edited individually. Examples are mirrored between the two pages they refer to, although it's possible to make an example asymmetric, in which case the two pages will show different content.
* The page view is interacive, so you don't have to open a separate page with the source, instead click on the "edit mode" button and every block gets its own edit button. Only the block currently being edited has its source displayed. After editing, the preview appears in the same block and can be saved or further edited.
* Sorting of examples.
* Automatic folderizing of examples (for side 0 pages only). The folder names are localizable.
* Dynamic suggestion box for the source and target pages of an example.
* Importer: fetch a page from tvtropes and extract the blocks/examples from it. Note that this might fail on many pages, it has only been tested on a handful of pages as seen in the `initialImport` function in `main.py`.
* Permissions: users can have roles and each role can have activities assigned to it.
* Red link handling: normally links to non-existing pages are not allowed. The user is offered the option to create the target pages (although regular users can only create side 1 pages). Mods can override the requirement and create red links. Furthermore a page can be set to be a permanent red link. These are still blocked from being linked to by regular users, but if a mod links to them, they get resolved and the resulting link will use the display name of the page.
* Multi-language support: each page, example and alias is associated with a language. For now only "en" and "es" are supported as languages. When visiting an alias, the language of the alias is used to determine which examples to display as well as the localization of the UI elements. The language can be overridden by adding `?lang=**` to the URL. For pages that have examples in multiple languages, language links are displayed at the top.
* Bulk edit, move and hide/unhide of examples.

# Concepts
* Page type: e.g. trope, YMMV, Trivia, work/creator, useful notes and admin.
* Side: a page's side determines whether it can be a source, target of an example or neither. Currently the side is determined by the page type, for example trope, YMMV and trivia are side 0, work is side 1 and useful notes and admin are side 2. Side 0 is the example source, side 1 is the target, and side 2 indicates a page that can't have examples.
* Alias: in fact pages don't have titles. An alias contains a path, display name and language, and can be primary or not. Non-primary aliases redirect to the primary alias for the same language with an "a.k.a." display.
* Example settings:
 * Playing With type
 * Hide: doesn't display the example unless "Include hidden examples" is checked. Even when checked the example is displayed in grey to distinguish it from regular examples. This is the equivalent of a commented-out example that can only be found by editing the page. The existence of hidden examples blocks the creation of examples with the same source/target/playing with combination, as the example should be unhidden first. If the example is also locked, this means no new examples can be created for that combination. (Moderators can bypass this restriction.)
 * Lock (mod-only): prevents editing the example.
 * Embargo (mod-only): prevents creation of new examples for the source/target combination, regardless of playing with type. Since Real Life is an actual page, "No Real Life Examples" can be enforced by creating a blank example with Real Life as the other side and hiding and embargoing it.
* Page settings (admin-only):
 * Ads (placeholder used in this demo app)
 * Lock: prevents editing examples associated with the page as well as moving examples to or from it
 * Fake redlink (see above)
 * Change page type. Note that changing the page type is blocked if it would change the page's side and there are existing examples. This is not possible to bypass even with admin rights.

# Missing features
* Persistence. All changes are lost when quitting the app.
* Account system. Instead a handful of example users with various permissions are created and you can freely switch between them using the "Switch User" link on any wiki page.
* Comment sections or anything related to the forums.
* Advanced searching/querying via the URL.
* Some page types and block types mentioned in the concept doc.
