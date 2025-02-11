import requests
import random
import webbrowser
import re

# --------------------------------------------------
# Global Variables and Utility Functions
# --------------------------------------------------

# Predefined prefixes for various commands
HOW_QUESTION_PREFIXES = ["how", "what are"]
IM_STATEMENT_PREFIXES = ["i am", "im", "i have", " i "]
SEARCH_QUESTION_PREFIXES = ["what", "who", "what is"]

# Global variable to store user input text (used in some functions)
user_input_text = ""

def remove_filler_words():
    """
    Remove common filler words from the global user_input_text.
    """
    filler_words = ["search", "for", "that", "this", "and", "small", "short", "long", "big"]
    global user_input_text
    for word in filler_words:
        if word in user_input_text:
            user_input_text = user_input_text.replace(word, "")

# List of Top-Level Domains for website detection
TLDs = [
    ".com", ".org", ".net", ".int", ".edu", ".gov", ".mil",
    ".dk", ".de", ".fr", ".uk", ".us", ".ca", ".au", ".nz", ".cn", ".jp", ".ru", ".br",
    ".za", ".es", ".it", ".nl", ".se", ".no", ".fi", ".pl", ".ch", ".be", ".at", ".gr",
    ".pt", ".mx", ".ar", ".in", ".id", ".sg", ".hk", ".tw", ".kr", ".vn", ".th", ".my",
    ".ae", ".sa", ".eg", ".tr", ".ir", ".pk", ".bd", ".ph", ".ng", ".ke", ".gh", ".cl",
    ".co", ".ve", ".pe", ".cz", ".hu", ".ro", ".sk", ".bg", ".lt", ".lv", ".ee", ".is",
    ".ua", ".by", ".rs", ".me", ".ba", ".mk", ".si", ".hr", ".mt", ".cy", ".lu", ".li",
    ".qa", ".om", ".kw", ".bh", ".lb", ".jo", ".sy", ".iq", ".ye", ".af", ".np", ".bt",
    ".mv", ".lk", ".mm", ".la", ".kh", ".bn", ".tl", ".uz", ".kz", ".tm", ".kg", ".tj",
    ".mn", ".mo", ".ps", ".zw", ".mu", ".sc", ".dj", ".er", ".mz", ".bw", ".na", ".zm",
    ".rw", ".bi", ".so", ".gm", ".sn", ".ml", ".gn", ".bf", ".tg", ".ne", ".mr", ".ci",
    ".cm", ".cf", ".td", ".ga", ".cg", ".cd", ".ao", ".gq", ".st", ".cv", ".km", ".mg",
    ".pn", ".tf", ".gp", ".mq", ".re", ".yt", ".pm", ".wf", ".nc", ".pf", ".sx", ".bq",
    ".gl", ".fo", ".ax", ".gg", ".je", ".im", ".gi", ".sh", ".io", ".as", ".nu", ".tv",
    ".ws", ".to", ".fm", ".pw", ".cc", ".tk", ".cx", ".nf", ".hm", ".gs", ".sb", ".vu",
    ".nr", ".ki", ".ck", ".wf", ".mh", ".pf", ".mp", ".gu", ".vi", ".pr", ".dm", ".ag",
    ".lc", ".vc", ".bb", ".tt", ".gd", ".kn", ".ai", ".ms", ".bm", ".bz", ".gy", ".sr",
    ".aw", ".cw", ".sx", ".bq", ".tf", ".fk", ".gs", ".sh", ".io", ".ac", ".bv", ".hm"
]

def open_website(domain, category):
    """
    Open the website at the given domain.
    If a category (or search query) is provided, it is appended to the URL.
    """
    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain
    if category:
        category = category.strip().replace(" ", "+")
        url = f"{domain}/{category}"
    else:
        url = domain
    print("Opening:", url)
    webbrowser.open(url)

def extract_domain(words):
    """
    Return the first word that appears to be a domain (contains a known TLD).
    """
    for word in words:
        clean_word = re.sub(r'[^\w\.]', '', word)
        for tld in TLDs:
            if tld in clean_word:
                return clean_word
    return None

def process_input(user_input):
    """
    Process the user input to extract a website domain and a search query.
    """
    words = user_input.split()
    domain = extract_domain(words)
    remove_filler_words()
    filtered_words = user_input_text.split()
    pattern = r'find\s+(.+)'
    match = re.search(pattern, user_input, re.IGNORECASE)
    if match:
        key = match.group(1)
    else:
        if domain:
            filtered_words = [w for w in filtered_words if domain not in w]
        key = " ".join(filtered_words)
    if key.strip() == domain or key.strip() == "":
        key = ""
    return domain, key

# --------------------------------------------------
# Wikipedia Search Functions
# --------------------------------------------------

def search_wikipedia(search_term):
    """
    Search Wikipedia for the search_term and return the title of the first result.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": search_term
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "query" in data and "search" in data["query"]:
        results = data["query"]["search"]
        if results:
            return results[0]["title"]
    return None

def get_summary(title, max_length=500):
    """
    Retrieve a summary for a Wikipedia article given its title.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "exintro": True,
        "explaintext": True,
        "titles": title
    }
    response = requests.get(url, params=params)
    data = response.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        summary = page.get("extract", "")
        return summary[:max_length]
    return "No summary available."

def search_wiki(query):
    """
    Use Wikipedia search to print the title and summary of the first article found.
    """
    summary_length = 1800
    search_term = query
    if "small" in search_term or "short" in search_term:
        if summary_length > 100:
            pass
        else:
            summary_length -= 900
    if "long" in search_term or "big" in search_term:
        if summary_length > 100:
            pass
        else:
            summary_length += 900
    remove_filler_words()
    title = search_wikipedia(search_term)
    if title:
        summary = get_summary(title, max_length=summary_length)
        print(f"Title: {title}\nSummary: {summary}")
    else:
        print("No results found.")

# --------------------------------------------------
# Conversational Processing Functions
# --------------------------------------------------

def process_how_question(text):
    """
    Process a "how" question by building a response.
    """
    global is_how_question, additional_text, to_ai, output
    if "you" in text:
        to_ai = True
    if to_ai:
        if has_are:
            output = form[1]
        else:
            output = form[0]
    for word in text.split():
        if is_how_question:
            additional_text = " " + word
        else:
            if word == "you" or "your" in word:
                is_how_question = True
    if need_sub:
        output += " is"
    output += sentiment[random.randint(0, 1)]
    output += additional_text + random.choice(question_suffixes)
    print(output)

def process_im_statement(text):
    """
    Process an "I'm" statement by evaluating sentiment.
    """
    print("U")
    im_form = ["how", "that is ", "that is so", "that's"]
    global positive_words, negative_words, positive_count, negative_count, is_positive, question_suffixes
    for word in text.split():
        if word in positive_words:
            positive_count += 1
        elif word in negative_words:
            negative_count += 1
    if positive_count >= negative_count:
        is_positive = True
        output = "how " + str(random.choice(positive_words)) + " to hear!" + random.choice(question_suffixes)
    else:
        is_positive = False
        output = "how " + str(random.choice(negative_words)) + " to hear!" + random.choice(question_suffixes)
    print(output)

# --------------------------------------------------
# Story Generation (Rewrite) Functionality
# --------------------------------------------------

def rewrite_story():
    """
    Generates a story based on a template and user-provided names.
    The user is prompted for input in the form:
       "add 2 dogs named bob, jeff"
    The function extracts:
       - The number (as a string) [e.g., "2"]
       - The type (e.g., "dogs")
       - The names (split by commas)
    It then reads a story template (from 'template.txt' if available) that should contain placeholders like [Character 0], [Character 1], etc.
    Those placeholders are replaced with the provided names.
    """
    user_story_input = input("User (story mode): ").lower()

    # --- Extract variables from user input ---
    words = user_story_input.split()
    try:
        add_index = words.index("add")
        characters = words[add_index + 1]  # e.g., "2"
        characters_amount = words[add_index + 2]  # e.g., "dogs"
    except (ValueError, IndexError):
        print("Input format incorrect. Please use: 'add <number> <type> named <name1>, <name2>, ...'")
        return ""
    
    try:
        named_index = words.index("named")
    except ValueError:
        print("Input must contain 'named' followed by the names.")
        return ""
    
    # Everything after "named" is treated as names (split by comma)
    names_str = " ".join(words[named_index + 1:])
    names = [name.strip() for name in names_str.split(",") if name.strip()]
    
    print("\nExtracted variables:")
    print("characters:", characters)
    print("CharactersAmmount:", characters_amount)
    print("names:", names)
    
    # --- Read the story template ---
    try:
        with open("template.txt", "r", encoding="ISO-8859-1") as f:
            template_text = f.read()
        # Decode from latin1 to utf-8 if necessary
        template_text = template_text.encode("latin1").decode("utf-8")
    except FileNotFoundError:
        print("File 'template.txt' not found. Using default template.")
        template_text = ("Once upon a time, [Character 0] went on an adventure. "
                         "[Character 1] joined [Character 0] and they discovered a magical land.")
    
    # --- Replace placeholders with names ---
    for i in range(6):
        if i < len(names):
            template_text = template_text.replace(f"[Character {i}]", names[i])
        else:
            # If not enough names are provided, replace with the first name or empty string
            template_text = template_text.replace(f"[Character {i}]", names[0] if names else "")
    
    return template_text

# --------------------------------------------------
# Main Interactive Loop
# --------------------------------------------------

while True:
    user_input_text = " " + input("Enter command: ").lower()

    # Reset variables for processing conversational input
    has_are = False
    if "are" in user_input_text:
        has_are = True
    additional_text = ""
    to_ai = False
    form = ["my", "im", "i am"]
    output = ""
    need_sub = False
    sentiment = [" good", " bad"]
    question_suffixes = [
        ". Can I help you with something?",
        ". Can I help you with anything else?",
        " Is there anything else I can help you with?"
    ]
    positive_words = ["great", "good", "fantastic"]
    negative_words = ["bad", "terrible", "horrible"]
    positive_count = 0
    negative_count = 0
    is_positive = False

    # Check if the user wants to trigger the story generation functionality.
    # This will happen if the input contains any of the trigger phrases.
    rewriting_triggers = ["rewrite", "write", "make me a story", "story"]
    if any(trigger in user_input_text for trigger in rewriting_triggers):
        result = rewrite_story()
        print("\nGenerated Story:")
        print(result)
    else:
        # Process "how" questions
        for word in HOW_QUESTION_PREFIXES:
            if word in user_input_text:
                process_how_question(user_input_text)
                break
        # Process "I'm" statements
        for word in IM_STATEMENT_PREFIXES:
            if word in user_input_text:
                process_im_statement(user_input_text)
                break
        # Process Wikipedia search queries
        for word in SEARCH_QUESTION_PREFIXES:
            if word in user_input_text:
                search_wiki(user_input_text)
                break
        # Process website search commands
        if "search" in user_input_text:
            domain, key = process_input(user_input_text)
            if domain:
                open_website(domain, key)
            else:
                print("Could not determine a valid website domain from your input.")
