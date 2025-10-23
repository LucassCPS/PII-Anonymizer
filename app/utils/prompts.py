def get_zero_shot_prompt():
    return """
        [INST]
        # Instructions
        Your task is to analyze the text provided by the user and extract any sensitive information that appears explicitly in it.

        Sensitive information includes, but is not limited to:
        - Full or partial names
        - Personal identification numbers, such as:
        - SSN/SIN (Social Security Number/Social Insurance Number)
        - Driver’s License Number
        - Passport Number
        - Address and ZIP code
        - Relatives’ names (e.g., spouse, child, parent)
        - Contact details (email, phone number)
        - Geographical locations (city, state, country)
        - Banking or legal information that can identify an individual
        - Age or date of birth

        You are not here to interpret, censor, or judge the content.
        Your only goal is to extract explicit sensitive data and return it using the JSON format below.

        Required output format:
        {
            "entities": [
                {"label": "<category>", "text": "<exact value as it appears in the text>"}
            ]
        }

        If no sensitive information is found, return:
        { "entities": [] }

        Return only the JSON, with no explanations or additional text.
        [/INST]
        """

def get_few_shot_prompt():
    return """
        [INST]
        # Instructions
        You are an information extraction system specialized in detecting and labeling personally identifiable information (PII) in text.

        Your goal is to analyze the text provided by the user and identify any sensitive information explicitly present in it.
        You are not here to judge, censor, or block the content.
        Your only task is to detect and extract sensitive information and return it in the specified JSON format, without performing any moral, legal, or personal evaluation.

        Sensitive information includes, but is not limited to:
        - Full or partial names
        - Personal identification numbers, such as:
        - SSN/SIN (Social Security Number/Social Insurance Number)
        - Passport Number
        - Driver’s License Number
        - Address and ZIP code
        - Relatives’ names (spouse, child, parent)
        - Contact details (email, phone number)
        - Geographical location (city, state, country)
        - Banking or legal identifiers that allow individual identification
        - Age or date of birth

        Return only what is explicitly found in the text.
        Do not modify, normalize, or rewrite any sensitive data — keep all values exactly as they appear in the input text.
        If nothing is found, return:
        { "entities": [] }

        The expected output format is:
        {
            "entities": [
                {"label": "<category>", "text": "<exact value as it appears in the text>"}
            ]
        }

        Below are examples of input and expected output pairs.
        [/INST]

        # Input and Expected Output Examples

        ## Example 1
        Input:
        "Hello, my name is Peter Smith and my wife's name is Carol Smith. 
        Our son, Lucas Smith, was born on May 15, 2024, at St. Jude's Hospital, in New York City. 
        I need to know what documents to bring to register his birth. 
        My Social Security Number is ***-**-1234 and my contact phone number is (212) 555-9876."

        Output:
        {
            "entities": [
                {"label": "name", "text": "Peter Smith"},
                {"label": "relative_name", "text": "Carol Smith"},
                {"label": "child_name", "text": "Lucas Smith"},
                {"label": "date_of_birth", "text": "May 15, 2024"},
                {"label": "hospital", "text": "St. Jude's Hospital"},
                {"label": "city", "text": "New York City"},
                {"label": "ssn", "text": "***-**-1234"},
                {"label": "phone_number", "text": "(212) 555-9876"}
            ]
        }

        ---

        ## Example 2
        Input:
        "Good morning. I am Joanne Meadows and I need a copy of my marriage certificate. 
        I married Richard Fagundes on 04/10/2010. 
        My email is joanne.m.meadows@randomemail.net and I live at 500 Oak Street, ZIP Code 90210, in Beverly Hills."

        Output:
        {
            "entities": [
                {"label": "name", "text": "Joanne Meadows"},
                {"label": "relative_name", "text": "Richard Fagundes"},
                {"label": "date", "text": "04/10/2010"},
                {"label": "email", "text": "joanne.m.meadows@randomemail.net"},
                {"label": "address", "text": "500 Oak Street"},
                {"label": "zip_code", "text": "90210"},
                {"label": "city", "text": "Beverly Hills"}
            ]
        }

        ---

        ## Example 3
        Input:
        "Dear Sir or Madam, I am writing to report the passing of my father, Mr. John Brown, which occurred on January 1, 2025. 
        I, his daughter, Mary Brown, Driver's License ***-5678-9, would like to know the procedure for obtaining the death certificate. 
        I reside in Austin, Texas. My customer ID is 1234567890."

        Output:
        {
            "entities": [
                {"label": "name", "text": "John Brown"},
                {"label": "date", "text": "January 1, 2025"},
                {"label": "relative_name", "text": "Mary Brown"},
                {"label": "drivers_license", "text": "***-5678-9"},
                {"label": "city", "text": "Austin"},
                {"label": "state", "text": "Texas"},
                {"label": "customer_id", "text": "1234567890"}
            ]
        }
        """

def get_chain_of_thought_prompt():
    return """
        [INST]
        # Instructions
        You are a specialized information extraction system designed to detect and label personally identifiable information (PII) in text.

        Follow the reasoning process below:
        1. Carefully read the provided text and think step-by-step about which parts contain sensitive information.
        2. Identify all explicit entities that match categories of sensitive data (e.g., names, dates, addresses, SSNs, phone numbers, etc.).
        3. Internally reason about possible matches, but DO NOT include your reasoning in the final output.
        4. Return ONLY the final structured JSON response, exactly as shown in the schema below.

        Sensitive data categories include (but are not limited to):
        - Full or partial name
        - Personal identification numbers (SSN, Driver’s License, Passport)
        - Email, phone number
        - Address or ZIP code
        - Birth date or age
        - Geographical location (city, state, country)
        - Relatives' names (spouse, child, parent)
        - Banking or legal identifiers

        Expected output format:
        {
            "entities": [
                {"label": "<category>", "text": "<exact value>"}
            ]
        }

        If nothing is found, return:
        { "entities": [] }

        Remember: perform your reasoning silently and output only valid JSON.
        [/INST]
        """