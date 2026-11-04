import streamlit as st
from config import DASHBOARD_NAME

CSS = """
<link rel="stylesheet" href="/showback-report/app/static/stylesheets/moj-frontend.min.css">
<link rel="stylesheet" href="/showback-report/app/static/stylesheets/govuk-frontend-5.1.0.min.css">

<style>
:root {
  --showback-footer-height: 16rem;
}

[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] :is(p, label, input, button, select, h1, h2, h3),
[data-testid="stSidebar"] :is(p, label, input, button, select, h1, h2, h3),
.govuk-footer {
  font-family: Arial, sans-serif;
  color: #0b0c0c;
}

[data-testid="stSidebar"] {
  background-color: #f3f2f1;
  border-right: 1px solid #b1b4b6;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] [role="combobox"],
[data-testid="stSidebar"] :is([data-testid="stSelectbox"], [data-testid="stMultiSelect"]) [role="group"],
[data-testid="stFileUploaderDropzone"],
[data-testid="stDataFrame"],
[data-testid="stDataFrameResizable"],
[data-testid="stDataFrame"] .stDataFrameGlideDataEditor {
  border-radius: 0;
}

[data-testid="stDataFrameResizable"] {
  border-radius: 0 !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div,
[data-testid="stSidebar"] :is([data-testid="stSelectbox"], [data-testid="stMultiSelect"]) [role="group"],
[data-testid="stFileUploaderDropzone"] {
  border: 1px solid #b1b4b6;
  background-color: #ffffff;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"],
[data-testid="stTabs"] [role="tab"][aria-selected="true"] .react-aria-SelectionIndicator {
  background-color: #1d70b8;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
  color: #1d70b8;
}

/* Replace Streamlit's fixed toolbar/header with the MoJ service header. */
[data-testid="stHeader"] {
  background: transparent;
  top: 5rem;
}

[data-testid="stToolbarActions"],
[data-testid="stMainMenu"],
[data-testid="stAppDeployButton"] {
  display: none;
}

#moj-header-root {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  z-index: 999999 !important;
  width: 100% !important;
  background-color: #0b0c0c !important;
}

.moj-header {
  background-color: #0b0c0c !important;
  color: white !important;
  padding: 0.75rem 1rem !important;
  border-bottom: 4px solid #1d70b8 !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.moj-header__container {
  display: flex !important;
  align-items: center !important;
  padding: 0 2rem !important;
  max-width: 100% !important;
  width: 100% !important;
}

.moj-header__logo {
  display: flex !important;
  align-items: center !important;
  gap: 1rem !important;
  width: 100% !important;
}

.moj-header__logotype-crest {
  width: 40px !important;
  height: 40px !important;
  display: block !important;
  flex-shrink: 0 !important;
}

.moj-header__link {
  color: white !important;
  text-decoration: none !important;
  font-size: 1.125rem !important;
  font-weight: 700 !important;
  display: inline !important;
}

.moj-header__link--organisation-name {
  font-size: 1rem !important;
  font-weight: 400 !important;
  margin: 0 0.5rem !important;
}

.moj-header__link--service-name {
  text-decoration: underline !important;
  font-size: 1rem !important;
  font-weight: 700 !important;
  margin-left: 0.5rem !important;
}

/* The sidebar is itself a fixed-position element, so it must be offset
   using `top`/`height`, not `margin-top`, or it will render underneath
   the header instead of being pushed down by it. */
[data-testid="stSidebar"] {
  position: fixed;
  top: 5rem;
  height: calc(100dvh - 5rem);
}

[data-testid="stMainBlockContainer"] {
  --showback-content-gutter: 5rem;
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
  padding-inline: var(--showback-content-gutter);
  padding-bottom: 0;
}

[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
  flex: 1;
}

[data-testid="stElementContainer"]:has(.govuk-footer) {
  margin-top: auto;
}

[data-testid="stMarkdownContainer"]:has(> .govuk-footer) {
  margin-bottom: 0;
}

.govuk-footer {
  position: static;
  width: calc(100% + 2 * var(--showback-content-gutter));
  margin-inline: calc(-1 * var(--showback-content-gutter));
  height: var(--showback-footer-height);
  box-sizing: border-box;
  padding-block: 2rem;
  border-top: 1px solid #b1b4b6;
  background-color: #f3f2f1;
  color: #0b0c0c;
  font-size: 1rem;
  line-height: 1.5;
  overflow-y: auto;
}

.govuk-footer > .govuk-width-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 100%;
  max-width: none;
  margin-inline: var(--showback-content-gutter, 1rem);
}

.govuk-footer .govuk-footer__crown {
  flex-shrink: 0;
}

.govuk-footer .govuk-footer__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 1rem 2rem;
  margin: 1rem 0 0;
}

.govuk-footer .govuk-footer__meta-item {
  margin: 0;
}

.govuk-footer .govuk-footer__meta-item--grow {
  flex: 1 1 28rem;
}

.govuk-footer .govuk-footer__licence-logo {
  margin-right: 0.5rem;
  vertical-align: middle;
}

.govuk-footer .govuk-footer__link {
  color: #0b0c0c;
  text-decoration: underline;
}

.govuk-footer .govuk-footer__copyright-logo {
  min-width: 0;
  padding-top: 0;
  background-image: none;
}

@media (max-width: 48rem) {
  :root {
    --showback-footer-height: 14rem;
  }

  [data-testid="stMainBlockContainer"] {
    --showback-content-gutter: 1rem;
  }
}

</style>
"""


def render_header() -> None:
  HEADER_HTML = f"""
<div id="moj-header-root">
  <header class="moj-header" role="banner">
    <div class="moj-header__container">
      <div class="moj-header__logo">
        <img src="/showback-report/app/static/images/moj-logotype-crest.png" alt=""
             width="40" height="40" class="moj-header__logotype-crest">
        <a class="moj-header__link moj-header__link--organisation-name" href="https://www.gov.uk/government/organisations/ministry-of-justice">
          Ministry of Justice
        </a>
        <a class="moj-header__link moj-header__link--service-name" href="/">
          {DASHBOARD_NAME}
        </a>
      </div>
    </div>
  </header>
</div>
"""

  st.markdown(CSS + HEADER_HTML, unsafe_allow_html=True,)


def render_footer() -> None:
  FOOTER_HTML = """
<div class="govuk-footer">
  <div class="govuk-width-container">
    <svg
      focusable="false"
      role="presentation"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 64 60"
      height="30"
      width="32"
      fill="currentcolor" class="govuk-footer__crown">
      <g>
        <circle cx="20" cy="17.6" r="3.7" />
        <circle cx="10.2" cy="23.5" r="3.7" />
        <circle cx="3.7" cy="33.2" r="3.7" />
        <circle cx="31.7" cy="30.6" r="3.7" />
        <circle cx="43.3" cy="17.6" r="3.7" />
        <circle cx="53.2" cy="23.5" r="3.7" />
        <circle cx="59.7" cy="33.2" r="3.7" />
        <circle cx="31.7" cy="30.6" r="3.7" />
        <path d="M33.1,9.8c.2-.1.3-.3.5-.5l4.6,2.4v-6.8l-4.6,1.5c-.1-.2-.3-.3-.5-.5l1.9-5.9h-6.7l1.9,5.9c-.2.1-.3.3-.5.5l-4.6-1.5v6.8l4.6-2.4c.1.2.3.3.5.5l-2.6,8c-.9,2.8,1.2,5.7,4.1,5.7h0c3,0,5.1-2.9,4.1-5.7l-2.6-8ZM37,37.9s-3.4,3.8-4.1,6.1c2.2,0,4.2-.5,6.4-2.8l-.7,8.5c-2-2.8-4.4-4.1-5.7-3.8.1,3.1.5,6.7,5.8,7.2,3.7.3,6.7-1.5,7-3.8.4-2.6-2-4.3-3.7-1.6-1.4-4.5,2.4-6.1,4.9-3.2-1.9-4.5-1.8-7.7,2.4-10.9,3,4,2.6,7.3-1.2,11.1,2.4-1.3,6.2,0,4,4.6-1.2-2.8-3.7-2.2-4.2.2-.3,1.7.7,3.7,3,4.2,1.9.3,4.7-.9,7-5.9-1.3,0-2.4.7-3.9,1.7l2.4-8c.6,2.3,1.4,3.7,2.2,4.5.6-1.6.5-2.8,0-5.3l5,1.8c-2.6,3.6-5.2,8.7-7.3,17.5-7.4-1.1-15.7-1.7-24.5-1.7h0c-8.8,0-17.1.6-24.5,1.7-2.1-8.9-4.7-13.9-7.3-17.5l5-1.8c-.5,2.5-.6,3.7,0,5.3.8-.8,1.6-2.3,2.2-4.5l2.4,8c-1.5-1-2.6-1.7-3.9-1.7,2.3,5,5.2,6.2,7,5.9,2.3-.4,3.3-2.4,3-4.2-.5-2.4-3-3.1-4.2-.2-2.2-4.6,1.6-6,4-4.6-3.7-3.7-4.2-7.1-1.2-11.1,4.2,3.2,4.3,6.4,2.4,10.9,2.5-2.8,6.3-1.3,4.9,3.2-1.8-2.7-4.1-1-3.7,1.6.3,2.3,3.3,4.1,7,3.8,5.4-.5,5.7-4.2,5.8-7.2-1.3-.2-3.7,1-5.7,3.8l-.7-8.5c2.2,2.3,4.2,2.7,6.4,2.8-.7-2.3-4.1-6.1-4.1-6.1h10.6,0Z" />
      </g>
    </svg>
    <div class="govuk-footer__meta">
      <div class="govuk-footer__meta-item govuk-footer__meta-item--grow">
        <svg
          aria-hidden="true"
          focusable="false"
          class="govuk-footer__licence-logo"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 483.2 195.7"
          height="17"
          width="41">
          <path
            fill="currentColor"
            d="M421.5 142.8V.1l-50.7 32.3v161.1h112.4v-50.7zm-122.3-9.6A47.12 47.12 0 0 1 221 97.8c0-26 21.1-47.1 47.1-47.1 16.7 0 31.4 8.7 39.7 21.8l42.7-27.2A97.63 97.63 0 0 0 268.1 0c-36.5 0-68.3 20.1-85.1 49.7A98 98 0 0 0 97.8 0C43.9 0 0 43.9 0 97.8s43.9 97.8 97.8 97.8c36.5 0 68.3-20.1 85.1-49.7a97.76 97.76 0 0 0 149.6 25.4l19.4 22.2h3v-87.8h-80l24.3 27.5zM97.8 145c-26 0-47.1-21.1-47.1-47.1s21.1-47.1 47.1-47.1 47.2 21 47.2 47S123.8 145 97.8 145" />
        </svg>
        <span class="govuk-footer__licence-description">
          All content is available under the
          <a
            class="govuk-footer__link"
            href="https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"
            rel="license">Open Government Licence v3.0</a>, except where otherwise stated
        </span>
      </div>
      <div class="govuk-footer__meta-item">
        <a
          class="govuk-footer__link govuk-footer__copyright-logo"
          href="https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/">
          © Crown copyright
        </a>
      </div>
    </div>
  </div>
</div>
"""

  st.markdown( FOOTER_HTML, unsafe_allow_html=True)
