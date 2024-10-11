import streamlit as st
import json
from io import StringIO, BytesIO

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
    'sc_deny_causal_extreme_weather_sentence': ('Denying climate change as a causal factor in extreme weather', 'Sub-claim'),
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

# Helper function to map current categorization to the claims list
def get_default_categorisation(claim_text, claim_type):
    for claim in claims_list:
        # Find the corresponding full string in claims_list that matches the claim text
        if claim.endswith(claim_text):
            return claim
    # Return 'Please Select' if no match is found
    return 'Please Select'

# File uploader for JSON format
uploaded_file = st.file_uploader("Upload Finalized JSON File", type="json")

if uploaded_file:
    # Read and load the JSON content
    json_file = StringIO(uploaded_file.getvalue().decode("utf-8"))
    json_data = json.load(json_file)

    if isinstance(json_data, list):
        articles = json_data
        updated_articles = []

        for index, article in enumerate(articles, start=1):
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
                    st.write(article[field]['S'])
                    st.markdown(f"**Categorisation:**  ")
                    st.markdown(f"**{claim_type}: {claim_text}**")

                    # Get the current categorization from the article
                    current_categorisation = claim_text

                    # Get the corresponding default categorisation from claims_list
                    default_categorisation = get_default_categorisation(claim_text, claim_type)

                    # Checkbox to edit categorization
                    edit_categorisation = st.checkbox(f"Edit Categorisation ?", key=f"edit_{index}_{sentence_count}")

                    if edit_categorisation:
                        # Set the dropdown default value based on current categorisation
                        new_categorisation = st.selectbox(f"Select different category for sentence {sentence_count}",
                                                          claims_list,
                                                          index=claims_list.index(default_categorisation),
                                                          key=f"select_{index}_{sentence_count}")

                        if new_categorisation in ['Broad Claims:', 'Sub-Claims:']:
                            st.error("Please select a valid claim, not a category header.")
                        else:
                            if new_categorisation != 'Please Select':
                                article[field]['S'] = new_categorisation

                    st.markdown("---")
                    sentence_count += 1

            st.markdown("### Submit a Missing Categorisation?")
            missing_categorisation = st.checkbox(f"Submit a Missing Categorisation?", key=f"missing_{index}")

            if missing_categorisation:
                st.markdown("**Please copy the exact sentence from the full text field and paste below, then select the relevant categorisation.**")
                missing_sentence = st.text_area("", key=f"missing_sentence_{index}")
                if not missing_sentence.strip():
                    st.error("This field is mandatory.")
                missing_claim = st.selectbox("**Select Category for Sentence**", claims_list, key=f"missing_claim_{index}")

                if missing_claim in ['Broad Claims:', 'Sub-Claims:']:
                    st.error("Please select a valid claim, not a category header.")
                elif missing_claim != 'Please Select' and missing_sentence.strip():
                    submit_another = st.checkbox("Submit Another Missing Categorisation?", key=f"submit_another_{index}")

                    if submit_another:
                        st.text_area("Enter the next sentence:", key=f"missing_sentence_another_{index}")
                        st.selectbox("Select Category for Next Sentence", claims_list, key=f"missing_claim_another_{index}")

            updated_articles.append(article)

        # Add custom CSS to center the button and make it green
        st.markdown("""
        <style>
        .save-button-container {
            display: flex;
            justify-content: center;
        }
        .stButton button {
            background-color: #28a745;
            color: white;
            padding: 10px 20px;  /* Adjust the padding for button size */
            font-size: 16px;      /* Adjust the font size */
            border: none;         /* Remove border */
            border-radius: 5px;  /* Add rounded corners */
            width: 180px;         /* Set a specific width */
            height: 45px;        /* Set a specific height */
        }
        </style>
        """, unsafe_allow_html=True)

        # Center the button using a container div
        with st.container():
            st.markdown('<div class="save-button-container">', unsafe_allow_html=True)
            if st.button('Save'):
                updated_json = json.dumps(updated_articles)
                updated_file = BytesIO(updated_json.encode())
                st.download_button(label="Download Updated JSON", data=updated_file, file_name="updated_articles.json")
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("Uploaded file is not in the expected format.")