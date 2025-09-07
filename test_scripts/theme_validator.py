import os

def validate_theme(theme_text: str) -> bool:
    theme_text = theme_text.lower()
    found_selectors = []

    required_selectors = {
        "#maincontainer", "#titlebar", "#titlelabel",
        "#titlebuttons qpushbutton", "#closebutton", "#minimizebutton",
        "#customtabwidget::pane", "#customtabwidget::tab-bar",
        "#customtabwidget qtabbar::tab", "#customtabwidget qtabbar::tab:selected",
        "#customtabwidget qtabbar::tab:hover:!selected",
        "qwidget#tabcontentwidget", "qscrollarea", "qscrollbar:vertical",
        "qscrollbar::handle:vertical", "qscrollbar::handle:vertical:hover",
        "qscrollbar::add-line:vertical", "qscrollbar::sub-line:vertical",
        "qgroupbox", "qgroupbox::title", "qlabel", "qlineedit",
        "qlineedit:focus", "qlineedit:disabled", "qcheckbox",
        "qcheckbox::indicator", "qcheckbox::indicator:checked",
        "qcheckbox::indicator:hover", "qpushbutton", "qpushbutton:hover",
        "qpushbutton:pressed", "qpushbutton:disabled", "#startbutton",
        "#startbutton:hover", "#stopbutton", "#stopbutton:hover",
        "#donatebutton", "#donatebutton:hover", "qlistwidget",
        "qlistwidget::item", "qlistwidget::item:selected",
        "qlistwidget::item:hover", "qtextedit", "#logwidget",
        "#filterframe", "qcombobox", "qcombobox:hover", "qcombobox:focus",
        "qcombobox::drop-down", "qcombobox::down-arrow",
        "qcombobox qabstractitemview", "qcombobox qabstractitemview::item",
        "qcombobox qabstractitemview::item:selected", "qframe", "qmessagebox",
        "qmessagebox qpushbutton", "#creditscontainer", "#developercard",
        "#developercard:hover", "#sectioncard", "#versionlabel",
        "#donatecardbutton", "#donatecardbutton:hover", "#donatecardbutton:pressed",
        "qdialog#popoutwindow", "qwidget#popoutconfigbox","qwidget#calibrationeditor",
        "qwidget#calibrationeditorcontent"
    }

    for sel in required_selectors:
        if sel in theme_text:
            found_selectors.append(sel)

    missing = sorted(req for req in required_selectors if req not in found_selectors)

    if missing:
        print(f"Theme validation failed. Missing selectors:\n" + "\n".join(missing))
        return False

    if theme_text.count('{') != theme_text.count('}'):
        print("Theme validation failed: mismatched curly braces.")
        return False

    return True


if __name__ == "__main__":
    _path = input("Insert the FULL PATH (c:\\users\\path\\to\\theme.ssthm): ")

    if not os.path.exists(_path):
        print("Path does not exist:")
    else:
        with open(_path, "r") as f:
            theme_content = f.read()

            validation = validate_theme(theme_content)

            if validation:
                print("Theme is valid!")
            else:
                print("Theme was not valid (did not contain all required items)")
