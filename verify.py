import streamlit as st
import json
import os
from io import StringIO
import re

# Define the title
st.title("Article Categorisation Verification Form")

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
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text.strip())
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

    highlighted_sentence = f"<b style='background-color: yellow;'>{sentences[target_index].strip()}</b>"

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

# Main application logic begins here
# file_uploader: dispaly a file uploader widget that allows user to select the file to upload.
#  Returns: None or UploadedFile or list of UploadedFile
# Initialize session state for storing changes and UI state
# Initialize session state for storing changes and UI state
if 'all_changes' not in st.session_state:
    st.session_state.all_changes = {}
if 'add_another' not in st.session_state:
    st.session_state.add_another = {}
if 'original_filename' not in st.session_state:
    st.session_state.original_filename = None

# Main application logic begins here
uploaded_file = st.file_uploader("Upload The JSON File", type="json")

if uploaded_file:
    # Store the original filename
    st.session_state.original_filename = uploaded_file.name

    json_file = StringIO(uploaded_file.getvalue().decode("utf-8"))
    json_data = json.load(json_file)

    if isinstance(json_data, list):
        articles = json_data

        for index, article in enumerate(articles, start=1):
            article_id = article['articleId']['N']
            if article_id not in st.session_state.all_changes:
                st.session_state.all_changes[article_id] = {}
            if article_id not in st.session_state.add_another:
                st.session_state.add_another[article_id] = False

            st.markdown('---')
            st.markdown(f"**Article Number: {index}**")
            st.markdown(f"**Headline**: {article['title']['S']}")

            col1, col2 = st.columns([0.15, 1])
            with col1:
                st.markdown("**Source**:")
            with col2:
                with st.expander("[reveal]", expanded=False):
                    st.write(f"{article['source']['S']}")

            col1, col2 = st.columns([0.15, 1])
            with col1:
                st.markdown("**Full Text**:")
            with col2:
                with st.expander("[reveal]", expanded=False):
                    st.write(f"{article['body']['S']}")

            sentence_count = 1

            for field, (claim_text, claim_type) in claim_mapping.items():
                if field in article:
                    st.markdown(f"**Sentence {sentence_count}:**")
                    full_text = article['body']['S']
                    target_sentence = article[field]['S']
                    sentence_with_context = get_sentence_context(full_text, target_sentence)
                    st.write(sentence_with_context, unsafe_allow_html=True)
                    st.markdown(f"**Current Categorisation:**  ")
                    st.markdown(f"**{claim_type}: {claim_text}**")

                    edit_categorisation = st.checkbox(f"Edit Categorisation ?",
                                                      key=f"edit_{article_id}_{sentence_count}")

                    if edit_categorisation:
                        current_claim = next((claim for claim in claims_list if claim.endswith(claim_text)), None)
                        current_claim_index = claims_list.index(current_claim) if current_claim else 0

                        new_categorisation = st.selectbox(
                            f"Select different category for sentence {sentence_count}, or remove",
                            claims_list,
                            index=current_claim_index,
                            key=f"select_{article_id}_{sentence_count}"
                        )

                        corresponding_field = claim_mapping_field_name.get(new_categorisation, "No corresponding field")

                        if new_categorisation in ['Broad Claims:', 'Sub-Claims:']:
                            st.error("Please select a valid claim, not a category header.")
                        elif new_categorisation == 'Remove sentence':
                            st.session_state.all_changes[article_id][field] = 'REMOVE'
                        elif new_categorisation != claim_text:
                            new_field = claim_mapping_field_name.get(new_categorisation)
                            if new_field:
                                st.session_state.all_changes[article_id][field] = {'new_field': new_field,
                                                                                   'sentence': target_sentence}

                    sentence_count += 1
                    st.markdown("---")

            st.markdown("### Submit a Missing Categorisation?")
            missing_categorisation = st.checkbox(f"Submit a Missing Categorisation?",
                                                 key=f"missing_categorisation_{article_id}")

            if missing_categorisation:
                st.markdown(
                    "**Please copy the exact sentence from the full text field and paste below, then select the relevant categorisation.**")
                missing_sentence = st.text_area("Enter a single sentence (mandatory)",
                                                key=f"missing_sentence_{article_id}")

                # Check and display reminder for multiple sentences
                if missing_sentence and not is_single_sentence(missing_sentence):
                    st.error("Please enter only one sentence. You have entered multiple sentences.")

                missing_claim = st.selectbox("**Select Category for Sentence**", claims_list,
                                             key=f"missing_claim_{article_id}")

                # Check and display reminder for invalid category selection
                if missing_claim in ['Broad Claims:', 'Sub-Claims:', 'Remove sentence']:
                    st.error(
                        "Please select a valid category. 'Broad Claims', 'Sub-Claims', and 'Remove sentence' are not valid selections.")

                if missing_sentence and missing_claim not in ['Broad Claims:', 'Sub-Claims:']:
                    if is_single_sentence(missing_sentence) and is_valid_category(missing_claim):
                        field_name = claim_mapping_field_name.get(missing_claim)
                        if field_name:
                            new_key = f'NEW_{field_name}'
                            st.session_state.all_changes[article_id][new_key] = {"S": missing_sentence}
                    else:
                        st.error("Please ensure you've entered a single sentence and selected a valid category.")

                add_another = st.checkbox("Submit Another Missing Categorisation?",
                                          key=f"add_another_{article_id}")

                if add_another:
                    st.markdown(
                        "**Please copy the exact sentence from the full text field and paste below, then select the relevant categorisation.**")
                    next_sentence = st.text_area("Enter a single sentence (mandatory)",
                                                 key=f"next_sentence_{article_id}")

                    # Check and display reminder for multiple sentences
                    if next_sentence and not is_single_sentence(next_sentence):
                        st.error("Please enter only one sentence. You have entered multiple sentences.")

                    next_claim = st.selectbox("**Select Category for Sentence**", claims_list,
                                              key=f"next_claim_{article_id}")

                    # Check and display reminder for invalid category selection
                    if next_claim in ['Broad Claims:', 'Sub-Claims:', 'Remove sentence']:
                        st.error(
                            "Please select a valid category. 'Broad Claims', 'Sub-Claims', and 'Remove sentence' are not valid selections.")

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
                            st.error("Please ensure you've entered a single sentence and selected a valid category.")

        st.markdown("""
        <style>
        .save-button-container {
            display: flex;
            justify-content: center;
        }
        .stButton button {
            background-color: #28a745; 
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            width: 180px;
            height: 45px;
        }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<div class="save-button-container">', unsafe_allow_html=True)
            if st.button('Save'):
                validation_errors = []
                all_valid = True

                for article_id, changes in st.session_state.all_changes.items():
                    for old_field, action in changes.items():
                        if isinstance(action, dict) and 'new_field' in action:
                            new_field = action['new_field']
                            sentence = action['sentence']
                            if not sentence.strip():
                                validation_errors.append(f"Article {article_id}, field {new_field}: Missing sentence.")
                                all_valid = False
                            if not is_single_sentence(sentence):
                                validation_errors.append(
                                    f"Article {article_id}, field {new_field}: Contains multiple sentences.")
                                all_valid = False
                            if not is_valid_category(new_field):
                                validation_errors.append(
                                    f"Article {article_id}, field {new_field}: Invalid category selected.")
                                all_valid = False
                        elif old_field.startswith('NEW_'):
                            new_field = old_field[4:]
                            if not is_valid_category(new_field):
                                validation_errors.append(
                                    f"Article {article_id}, new field {new_field}: Invalid category selected.")
                                all_valid = False
                            if isinstance(action["S"], list):
                                for sent in action["S"]:
                                    if not sent.strip():
                                        validation_errors.append(
                                            f"Article {article_id}, new field {new_field}: Missing sentence.")
                                        all_valid = False
                                    if not is_single_sentence(sent):
                                        validation_errors.append(
                                            f"Article {article_id}, new field {new_field}: Contains a multi-sentence entry.")
                                        all_valid = False
                            elif not action["S"].strip():
                                validation_errors.append(
                                    f"Article {article_id}, new field {new_field}: Missing sentence.")
                                all_valid = False
                            elif not is_single_sentence(action["S"]):
                                validation_errors.append(
                                    f"Article {article_id}, new field {new_field}: Contains multiple sentences.")
                                all_valid = False

                if validation_errors:
                    st.error("Validation errors found:")
                    for error in validation_errors:
                        st.error(error)
                    st.error(
                        "Cannot generate JSON file due to validation errors. Please ensure all entries contain a single sentence and have a valid category selected.")
                elif all_valid:
                    updated_articles = []
                    for article in articles:
                        article_id = article['articleId']['N']
                        if article_id in st.session_state.all_changes:
                            changes = st.session_state.all_changes[article_id]
                            for old_field, action in changes.items():
                                if action == 'REMOVE':
                                    article.pop(old_field, None)
                                elif isinstance(action, dict) and 'new_field' in action:
                                    new_field = action['new_field']
                                    sentence = action['sentence']
                                    article[new_field] = {"S": sentence}
                                    if old_field in article:
                                        article.pop(old_field, None)
                                elif old_field.startswith('NEW_'):
                                    new_field = old_field[4:]
                                    if new_field in article:
                                        if isinstance(article[new_field]['S'], list):
                                            if action["S"] not in article[new_field]['S']:
                                                article[new_field]['S'].append(action["S"])
                                        else:
                                            if article[new_field]['S'] != action["S"]:
                                                article[new_field]['S'] = [article[new_field]['S'], action["S"]]
                                    else:
                                        article[new_field] = {"S": action["S"]}
                        updated_articles.append(article)

                    json_output = json.dumps(updated_articles, indent=4)

                    # Generate the new filename
                    if st.session_state.original_filename:
                        base_name, ext = os.path.splitext(st.session_state.original_filename)
                        new_filename = f"{base_name}_updated{ext}"
                    else:
                        new_filename = "updated_articles.json"

                    st.download_button("Download Updated JSON", json_output,
                                       file_name=new_filename, mime="application/json")
                    st.success("All changes are valid. You can now download the updated JSON file.")
                else:
                    st.error(
                        "Cannot generate JSON file due to validation errors. Please ensure all entries contain a single sentence and have a valid category selected.")
            st.markdown('</div>', unsafe_allow_html=True)
