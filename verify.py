import streamlit as st
import json
import os
from io import StringIO
import re
import urllib


# Mapping of fields to claims and whether they are broad claims or sub-claims
claim_mapping = {
    'bc_gw_not_happening_sentence': ('Global Warming is Not Happening', 'Broad claim'),
    'bc_not_caused_by_human_sentence': ('Global Warming is Not Caused by Human Activity', 'Broad claim'),
    'bc_impacts_not_bad_sentence': ('Climate Impacts are Not Bad', 'Broad claim'),
    'bc_solutions_wont_work_sentence': ('Climate Solutions Won’t Work', 'Broad claim'),
    'bc_science_movement_unrel_sentence': ('Climate Science/Movement is Unreliable', 'Broad claim'),
    'bc_individual_action_sentence': ('Climate Change should be addressed by individual action', 'Broad claim'),
    'sc_cold_event_denial_sentence': ('Using isolated cold weather events to deny warming', 'Sub-claim'),
    'sc_deny_extreme_weather_sentence': ('Denying the increase in extreme weather events', 'Sub-claim'),
    'sc_deny_causal_extreme_weather_sentence': (
    'Denying climate change as a causal factor in extreme weather', 'Sub-claim'),
    'sc_natural_variations_sentence': ('Global warming is due to natural variations', 'Sub-claim'),
    'sc_past_climate_reference_sentence': ('Global warming is natural by referring to past events', 'Sub-claim'),
    'sc_species_adapt_sentence': ('Species can adapt to climate change', 'Sub-claim'),
    'sc_downplay_warming_sentence': ('Downplaying the significance of a few degrees of warming', 'Sub-claim'),
    'sc_policies_negative_sentence': ('Climate policies cause negative side effects', 'Sub-claim'),
    'sc_policies_ineffective_sentence': ('Climate policies are ineffective', 'Sub-claim'),
    'sc_policies_difficult_sentence': ('Addressing climate change is too difficult or impractical', 'Sub-claim'),
    'sc_low_support_policies_sentence': ('Low public support for climate policies', 'Sub-claim'),
    'sc_clean_energy_unreliable_sentence': ('Clean energy technologies are unreliable', 'Sub-claim'),
    'sc_climate_science_unrel_sentence': ('Climate science is unreliable or invalid', 'Sub-claim'),
    'sc_no_consensus_sentence': ('Lack of scientific consensus', 'Sub-claim'),
    'sc_movement_unreliable_sentence': ('Climate movement is unreliable', 'Sub-claim'),
    'sc_hoax_conspiracy_sentence': ('Climate change is a deliberate hoax or conspiracy', 'Sub-claim'),
    'think_tank_ref_sentence': ('Think Tank Reference', 'Think Tank Reference')
}

# Full list of claims for the dropdown, including 'Please Select' at the start
claims_list = [
    'Broad Claims:',
    '1. Global Warming is Not Happening',
    '2. Global Warming is Not Caused by Human Activity',
    '3. Climate Impacts are Not Bad',
    '4. Climate Solutions Won’t Work',
    '5. Climate Science/Movement is Unreliable',
    '6. Climate Change should be addressed by individual action',
    'Sub-Claims:',
    '1. Using isolated cold weather events to deny warming',
    '2. Denying the increase in extreme weather events',
    '3. Denying climate change as a causal factor in extreme weather',
    '4. Global warming is due to natural variations',
    '5. Global warming is natural by referring to past events',
    '6. Species can adapt to climate change',
    '7. Downplaying the significance of a few degrees of warming',
    '8. Climate policies cause negative side effects',
    '9. Climate policies are ineffective',
    '10. Addressing climate change is too difficult or impractical',
    '11. Low public support for climate policies',
    '12. Clean energy technologies are unreliable',
    '13. Climate science is unreliable or invalid',
    '14. Lack of scientific consensus',
    '15. Climate movement is unreliable',
    '16. Climate change is a deliberate hoax or conspiracy',
    'Think Tank Reference',
    'Remove sentence'
]

claim_mapping_field_name = {
    '1. Global Warming is Not Happening': 'bc_gw_not_happening_sentence',
    '2. Global Warming is Not Caused by Human Activity': 'bc_not_caused_by_human_sentence',
    '3. Climate Impacts are Not Bad': 'bc_impacts_not_bad_sentence',
    '4. Climate Solutions Won’t Work': 'bc_solutions_wont_work_sentence',
    '5. Climate Science/Movement is Unreliable': 'bc_science_movement_unrel_sentence',
    '6. Climate Change should be addressed by individual action': 'bc_individual_action_sentence',
    '1. Using isolated cold weather events to deny warming': 'sc_cold_event_denial_sentence',
    '2. Denying the increase in extreme weather events': 'sc_deny_extreme_weather_sentence',
    '3. Denying climate change as a causal factor in extreme weather': 'sc_deny_causal_extreme_weather_sentence',
    '4. Global warming is due to natural variations': 'sc_natural_variations_sentence',
    '5. Global warming is natural by referring to past events': 'sc_past_climate_reference_sentence',
    '6. Species can adapt to climate change': 'sc_species_adapt_sentence',
    '7. Downplaying the significance of a few degrees of warming': 'sc_downplay_warming_sentence',
    '8. Climate policies cause negative side effects': 'sc_policies_negative_sentence',
    '9. Climate policies are ineffective': 'sc_policies_ineffective_sentence',
    '10. Addressing climate change is too difficult or impractical': 'sc_policies_difficult_sentence',
    '11. Low public support for climate policies': 'sc_low_support_policies_sentence',
    '12. Clean energy technologies are unreliable': 'sc_clean_energy_unreliable_sentence',
    '13. Climate science is unreliable or invalid': 'sc_climate_science_unrel_sentence',
    '14. Lack of scientific consensus': 'sc_no_consensus_sentence',
    '15. Climate movement is unreliable': 'sc_movement_unreliable_sentence',
    '16. Climate change is a deliberate hoax or conspiracy': 'sc_hoax_conspiracy_sentence',
    'Think Tank Reference': 'think_tank_ref_sentence'
}


def is_single_sentence(text):
    # Remove leading/trailing whitespace
    text = text.strip()

    # Use a more robust regex to split sentences
    sentences = re.split(r'(?<=[.!?])\s*(?=[A-Z])', text)

    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]

    # Check if there's only one sentence
    return len(sentences) == 1

# Helper function to check if a category is valid
def is_valid_category(category):
    return category not in ['Broad Claims:', 'Sub-Claims:', 'Remove sentence']

def get_sentence_context(full_text, target_sentence):
    sentences = re.split(r'(?<=[.!?])\s*', full_text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    target_index = next((i for i, sentence in enumerate(sentences) if target_sentence.strip() in sentence), None)

    if target_index is None:
        return ""

    highlighted_sentence = f"<b style='background-color: #e80000;'>{sentences[target_index].strip()}</b>"

    if target_index == 0:
        next_sentence = sentences[target_index + 1].strip() if len(sentences) > 1 else ''
        return f"{highlighted_sentence} {next_sentence}".strip()
    elif target_index == len(sentences) - 1:
        previous_sentence = sentences[target_index - 1].strip()
        return f"{previous_sentence} {highlighted_sentence}".strip()
    else:
        previous_sentence = sentences[target_index - 1].strip()
        next_sentence = sentences[target_index + 1].strip()
        return f"{previous_sentence} {highlighted_sentence} {next_sentence}".strip()

st.markdown("""
<style>
    .stApp {
        background-color: black;
        color: white;
    }
    .title {
        color: white;
        font-size: 22px;
    }
    .article_number {
        background-color: #0236cd;
        color: white;
        padding: 5px;
    }
    .headline {
        font-size: 16px;
        color: white;
    }
    .sentence-text {
        font-size: 17px;
        color: white;
    }
    .categorisation-head {
        font-size: 17px;
        color: white;
    }
    .categorisation-text {
        font-size: 17px;
        color: white;
        background: #21232b;
    }
    .source, .full-text, .edit-categorisation, .select-category {
        color: white;
    }
    .stButton > button {
        color: white;
        background-color: #0236cd;
    }
    .stSelectbox, .stTextArea {
        color: white;
    }
    .streamlit-expanderHeader, .streamlit-expanderContent {
        color: white !important;
    }
    .missing-categorisation {
        color: white;
    }
    .error-message {
        color: red;
    }
    .save-button button {
        background-color: green !important;
        color: white !important;
    }
    .download-button {
        background-color: black !important;
        color: white !important;
        border: 1px solid white !important;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        text-decoration: none;
        display: inline-block;
        transition: background-color 0.3s, color 0.3s;
    }
    .download-button:hover {
        background-color: #e80000 !important;
        color: white !important;
        text-decoration: none;
    }
    .save-button-container {
        display: flex;
        justify-content: center;
    }
    .stButton button {
        background-color: #28a745; 
        color: white;
        padding: 10px 20px;
        font-size: 18px;
        border: none;
        border-radius: 5px;
        width: 180px;
        height: 45px;
    }
</style>
""", unsafe_allow_html=True)


# Main application logic begins here
# file_uploader: dispaly a file uploader widget that allows user to select the file to upload.
#  Returns: None or UploadedFile or list of UploadedFile
# Initialize session state for storing changes and UI state
# Define the title with white color
st.markdown('<h1 class="title">Article Categorisation Verification Form</h1>', unsafe_allow_html=True)

# Main application logic begins here
if 'all_changes' not in st.session_state:
    st.session_state.all_changes = {}
if 'add_another' not in st.session_state:
    st.session_state.add_another = {}
if 'original_filename' not in st.session_state:
    st.session_state.original_filename = None

uploaded_file = st.file_uploader("", type="json")

if uploaded_file:
    st.session_state.original_filename = uploaded_file.name
    json_file = StringIO(uploaded_file.getvalue().decode("utf-8"))
    json_data = json.load(json_file)

    if isinstance(json_data, list):
        articles = json_data

        for index, article in enumerate(articles, start=1):
            article_id = article['articleId']['N']
            print(f"Processing article {article_id}")  # Debug
            if article_id not in st.session_state.all_changes:
                st.session_state.all_changes[article_id] = {}
            if article_id not in st.session_state.add_another:
                st.session_state.add_another[article_id] = False

            st.markdown('---')
            st.markdown(f'<p class="article_number">Article Number: {index}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="headline"><strong>Headline</strong>: {article["title"]["S"]}</p>', unsafe_allow_html=True)

            col1, col2 = st.columns([0.15, 1])
            with col1:
                st.markdown('<p class="source"><strong>Source:</strong></p>', unsafe_allow_html=True)
            with col2:
                with st.expander("[reveal]", expanded=False):
                    st.markdown(f'<p class="source">{article["source"]["S"]}</p>', unsafe_allow_html=True)

            col1, col2 = st.columns([0.15, 1])
            with col1:
                st.markdown('<p class="full-text"><strong>Full Text:</strong></p>', unsafe_allow_html=True)
            with col2:
                with st.expander("[reveal]", expanded=False):
                    st.markdown(f'<p class="full-text">{article["body"]["S"]}</p>', unsafe_allow_html=True)

            sentence_count = 1

            for field in article.keys():
                if field in claim_mapping:
                    print(f"Found field: {field}")  # Debug
                    print(f"Sentence: {article[field]['S']}")  # Debug
                    claim_text, claim_type = claim_mapping[field]
                    st.markdown(f'<p class="sentence-text"><strong>Sentence {sentence_count}:</strong></p>', unsafe_allow_html=True)
                    full_text = article['body']['S']
                    target_sentence = article[field]['S']
                    sentence_with_context = get_sentence_context(full_text, target_sentence)
                    st.markdown(f'<p class="sentence-text">{sentence_with_context}</p>', unsafe_allow_html=True)

                    st.markdown('<p class="categorisation-head"><strong>Categorisation:</strong></p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="categorisation-text"><strong>{claim_type}</strong>: {claim_text}</p>', unsafe_allow_html=True)

                    st.markdown('<p class="edit-categorisation"><strong>Edit Categorisation?</strong></p>', unsafe_allow_html=True)
                    edit_categorisation = st.checkbox("", key=f"edit_{article_id}_{sentence_count}")

                    if edit_categorisation:
                        current_claim = next((claim for claim in claims_list if claim.endswith(claim_text)), None)
                        current_claim_index = claims_list.index(current_claim) if current_claim else 0

                        st.markdown(
                            f'<p class="select-category">Select different category for sentence {sentence_count}, or remove</p>',
                            unsafe_allow_html=True)
                        new_categorisation = st.selectbox("",
                                                          claims_list,
                                                          index=current_claim_index,
                                                          key=f"select_{article_id}_{sentence_count}"
                                                          )

                        if new_categorisation in ['Broad Claims:', 'Sub-Claims:']:
                            st.markdown(
                                '<p class="error-message">Please select a specific claim, not "Broad Claims" or "Sub-Claims".</p>',
                                unsafe_allow_html=True)
                        elif new_categorisation == 'Remove sentence':
                            st.session_state.all_changes[article_id][field] = 'REMOVE'
                        elif new_categorisation != claim_text:
                            new_field = claim_mapping_field_name.get(new_categorisation)
                            if new_field:
                                st.session_state.all_changes[article_id][field] = {'new_field': new_field,
                                                                                   'sentence': target_sentence}

                    sentence_count += 1
                    st.markdown("---")

            st.markdown('<h3 class="missing-categorisation">Submit a Missing Categorisation?</h3>', unsafe_allow_html=True)
            missing_categorisation = st.checkbox("", key=f"missing_categorisation_{article_id}")

            if missing_categorisation:
                st.markdown(
                    '<p class="instruction">Please copy the exact sentence from the full text field and paste below, then select the relevant categorisation.</p>',
                    unsafe_allow_html=True
                )
                missing_sentence = st.text_area("Enter a single sentence (mandatory)",
                                                key=f"missing_sentence_{article_id}")

                if missing_sentence and not is_single_sentence(missing_sentence):
                    st.markdown('<p class="error-message">Please enter only one sentence. You have entered multiple sentences.</p>', unsafe_allow_html=True)

                missing_claim = st.selectbox("Select Category for Sentence", claims_list,
                                             key=f"missing_claim_{article_id}")

                if missing_claim in ['Broad Claims:', 'Sub-Claims:', 'Remove sentence']:
                    st.markdown('<p class="error-message">Please select a valid category. \'Broad Claims\', \'Sub-Claims\', and \'Remove sentence\' are not valid category.</p>', unsafe_allow_html=True)

                if missing_sentence and missing_claim not in ['Broad Claims:', 'Sub-Claims:']:
                    if is_single_sentence(missing_sentence) and is_valid_category(missing_claim):
                        field_name = claim_mapping_field_name.get(missing_claim)
                        if field_name:
                            new_key = f'NEW_{field_name}'
                            st.session_state.all_changes[article_id][new_key] = {"S": missing_sentence}
                    else:
                        st.markdown('<p class="error-message">Please ensure you\'ve entered a single sentence and selected a valid category.</p>', unsafe_allow_html=True)

                st.markdown('<p class="add-another"><strong>Submit Another Missing Categorisation?</strong></p>', unsafe_allow_html=True)
                add_another = st.checkbox("", key=f"add_another_{article_id}")

                if add_another:
                    st.markdown(
                        '<p class="instruction">Please copy the exact sentence from the full text field and paste below, then select the relevant categorisation.</p>',
                        unsafe_allow_html=True
                    )
                    next_sentence = st.text_area("Enter a single sentence (mandatory)",
                                                 key=f"next_sentence_{article_id}")

                    if next_sentence and not is_single_sentence(next_sentence):
                        st.markdown('<p class="error-message">Please enter only one sentence. You have entered multiple sentences.</p>', unsafe_allow_html=True)

                    next_claim = st.selectbox("Select Category for Sentence", claims_list,
                                              key=f"next_claim_{article_id}")

                    if next_claim in ['Broad Claims:', 'Sub-Claims:', 'Remove sentence']:
                        st.markdown('<p class="error-message">Please select a valid category. \'Broad Claims\', \'Sub-Claims\', and \'Remove sentence\' are not valid selections.</p>', unsafe_allow_html=True)

                    if next_sentence and next_claim not in ['Broad Claims:', 'Sub-Claims:']:
                        if is_single_sentence(next_sentence) and is_valid_category(next_claim):
                            field_name = claim_mapping_field_name.get(next_claim)
                            if field_name:
                                new_key = f'NEW_{field_name}'
                                if new_key in st.session_state.all_changes[article_id]:
                                    if isinstance(st.session_state.all_changes[article_id][new_key]["S"], list):
                                        if next_sentence not in st.session_state.all_changes[article_id][new_key]["S"]:
                                            st.session_state.all_changes[article_id][new_key]["S"].append(next_sentence)
                                    else:
                                        if st.session_state.all_changes[article_id][new_key]["S"] != next_sentence:
                                            st.session_state.all_changes[article_id][new_key]["S"] = [
                                                st.session_state.all_changes[article_id][new_key]["S"],
                                                next_sentence
                                            ]
                                else:
                                    st.session_state.all_changes[article_id][new_key] = {"S": next_sentence}
                        else:
                            st.markdown('<p class="error-message">Please ensure you\'ve entered a single sentence and selected a valid category.</p>', unsafe_allow_html=True)

        print("All changes:")  # Debug
        print(json.dumps(st.session_state.all_changes, indent=2))  # Debug

        with st.container():
            st.markdown('<div class="save-button-container">', unsafe_allow_html=True)
            if st.button('Save', key='save_button'):
                validation_errors = []
                all_valid = True

                # Validation code remains the same...

                if validation_errors:
                    st.error("Validation errors found:")
                    for error in validation_errors:
                        st.markdown(f'<p class="error-message">{error}</p>', unsafe_allow_html=True)
                    st.markdown(
                        '<p class="error-message">Cannot generate JSON file due to validation errors. Please ensure all entries contain a single sentence and have a valid category selected.</p>',
                        unsafe_allow_html=True)
                elif all_valid:
                    updated_articles = []
                    for article in articles:
                        article_id = article['articleId']['N']
                        # Create a deep copy of the original article to preserve all fields
                        updated_article = {k: v.copy() if isinstance(v, dict) else v for k, v in article.items()}

                        if article_id in st.session_state.all_changes:
                            changes = st.session_state.all_changes[article_id]
                            print(f"Applying changes to article {article_id}")  # Debug

                            # First, handle all existing fields and their changes
                            fields_to_remove = set()  # Track fields that need to be removed
                            fields_to_add = {}  # Track new fields and their values

                            # Process all existing claim fields
                            for field in article.keys():
                                if field in claim_mapping:
                                    if field in changes:
                                        if changes[field] == 'REMOVE':
                                            fields_to_remove.add(field)
                                        elif isinstance(changes[field], dict) and 'new_field' in changes[field]:
                                            new_field = changes[field]['new_field']
                                            sentence = changes[field]['sentence']
                                            fields_to_add[new_field] = {"S": sentence}
                                            if field != new_field:
                                                fields_to_remove.add(field)
                                    else:
                                        # Keep the original field and value if no changes
                                        updated_article[field] = article[field]

                            # Remove fields marked for removal
                            for field in fields_to_remove:
                                updated_article.pop(field, None)

                            # Add new field values
                            for field, value in fields_to_add.items():
                                updated_article[field] = value

                            # Process new categorizations
                            for field, value in changes.items():
                                if field.startswith('NEW_'):
                                    new_field = field[4:]
                                    if new_field in updated_article:
                                        current_value = updated_article[new_field]['S']
                                        new_value = value["S"]

                                        # Handle both single values and lists
                                        if isinstance(current_value, list):
                                            if isinstance(new_value, list):
                                                current_value.extend(s for s in new_value if s not in current_value)
                                            elif new_value not in current_value:
                                                current_value.append(new_value)
                                        else:
                                            if isinstance(new_value, list):
                                                updated_article[new_field]['S'] = [current_value] + [s for s in
                                                                                                     new_value if
                                                                                                     s != current_value]
                                            elif new_value != current_value:
                                                updated_article[new_field]['S'] = [current_value, new_value]
                                    else:
                                        updated_article[new_field] = {"S": value["S"]}

                        updated_articles.append(updated_article)

                    # Debug print to check the content of updated articles
                    print("Updated articles content:")
                    for article in updated_articles:
                        print(json.dumps(article, indent=2))

                    json_output = json.dumps(updated_articles, indent=4)

                    if st.session_state.original_filename:
                        base_name, ext = os.path.splitext(st.session_state.original_filename)
                        new_filename = f"{base_name}_updated{ext}"
                    else:
                        new_filename = "updated_articles.json"

                    download_link = f'<a href="data:application/json;charset=utf-8,{urllib.parse.quote(json_output)}" download="{new_filename}" class="download-button">Download Updated JSON</a>'
                    st.markdown(download_link, unsafe_allow_html=True)

                    st.success("All changes are valid. You can now download the updated JSON file.")
                else:
                    st.markdown(
                        '<p class="error-message">Cannot generate JSON file due to validation errors. Please ensure all entries contain a single sentence and have a valid category selected.</p>',
                        unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
