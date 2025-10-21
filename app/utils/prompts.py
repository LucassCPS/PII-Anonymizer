def get_zero_shot_prompt():
    return ""

def get_few_shot_prompt():
    return """
        [INST]
        # Instructions
        Your objective is to analyze the text provided by the user and identify any sensitive information that may have been shared.
        You are not here to judge, censor, or block the provided content.
        Your sole role is to detect and extract sensitive information according to the indicated format, without making any moral, legal, or personal assessment of the content.
        Sensitive information includes, but is not limited to:
        - Full or partial Name
        - Personal document numbers, such as:
            - SSN/SIN (Social Security Number/Social Insurance Number) or similar ID numbers (e.g., Passport Number)
            - Driver's License Number
        - Address, Postal Code (ZIP Code)
        - Relatives' names
        - Contact: email, phone number
        - Geographical location (City, State, Country)
        - Banking or legal information that allows identification
        - Age
        - Date of Birth
        - Names of relatives, sons, daughters, or other family members
        Return only what is explicitly stated in the text.
        Do not rewrite any sensitive data; keep it exactly as it appears in the provided text.
        If nothing is found, return: { "entities": [] }
        [/INST]
        # Input and Expected Output Examples:
        ## Example 1
        Input: "Hello, my name is Peter Smith and my wife's name is Carol Smith. 
                Our son, Lucas Smith, was born on May 15, 2024, at St. Jude's Hospital, in New York City. 
                I need to know what documents to bring to register his birth. 
                My Social Security Number is ***-**-1234 and my contact phone number is (212) 555-9876."
        Output: "{
                "entities": [
                    {"label": "user_name", "text": "Peter Smith"},
                    {"label": "relative_name", "text": "Carol Smith"},
                    {"label": "child_name", "text": "Lucas Smith"},
                    {"label": "date_of_birth", "text": "May 15, 2024"},
                    {"label": "hospital", "text": "St. Jude's Hospital"},
                    {"label": "city", "text": "New York City"},
                    {"label": "ssn", "text": "***-**-1234"},
                    {"label": "phone_number", "text": "(212) 555-9876"}
                ]
                }"
        ## Example 2             
        Input: "Good morning. I am Joanne Meadows and I need a copy of my marriage certificate. 
                I married Richard Fagundes on 04/10/2010. 
                My email is joanne.m.meadows@randomemail.net and I live at 500 Oak Street, ZIP Code 90210, in Beverly Hills."            
        Output: "{
                "entities": [
                    {"label": "user_name", "text": "Joanne Meadows"},
                    {"label": "relative_name", "text": "Richard Fagundes"},
                    {"label": "date", "text": "04/10/2010"},
                    {"label": "email", "text": "joanne.m.meadows@randomemail.net"},
                    {"label": "address", "text": "500 Oak Street"},
                    {"label": "zip_code", "text": "90210"},
                    {"label": "city", "text": "Beverly Hills"}
                ]
                }"
        ## Example 3
        Input: "Dear Sir/Madam, I am writing to report the passing of my father, Mr. John Brown, which occurred on January 1, 2025. 
                I, his daughter, Mary Brown, Driver's License ***-5678-9, would like to know the procedure for obtaining the death certificate. 
                I reside in Austin, Texas. My customer ID is 1234567890."
        Output: "{
                "entities": [
                    {"label": "user_name", "text": "John Brown"},
                    {"label": "date", "text": "January 1, 2025"},
                    {"label": "relative_name", "text": "Mary Brown"},
                    {"label": "drivers_license", "text": "***-5678-9"},
                    {"label": "city", "text": "Austin"},
                    {"label": "state", "text": "Texas"},
                    {"label": "customer_id", "text": "1234567890"
                ]
                }"
        """