import nltk
from nltk.corpus import wordnet as wn
import matplotlib.pyplot as plt
import networkx as nx

try:
    wn.all_synsets()
except LookupError:
    nltk.download('wordnet')

global sysnsets 

def new_synsets(word):
    """
    Retrieve synsets for a given word in English.
    
    Args:
        word (str): The word to find synsets for
        
    Returns:
        list: A list of synset objects if found, None otherwise
    """
    synsets = wn.synsets(word, lang='eng')

    if not synsets:
        print(f"No synset for '{word}' found")
        return
    
    return synsets

def explore_synonymous(word):
    """
    Display detailed information about all synsets for a given word.
    
    For each synset, prints:
    - Name and part of speech
    - Definition
    - Synonyms (lemma names)
    - Usage examples if available
    
    Args:
        word (str): The word to explore synonyms for
    """
    global synsets
    
    print(f"\n=== Synsets for '{word}': ===")

    for i, syn in enumerate(synsets):
        print(f"{i+1}. {syn.name()} ({syn.pos()}): {syn.definition()}")
        
        lemmas = syn.lemma_names()

        if lemmas:
            print(f"   Synonyms: {', '.join(lemmas)}")
        
        examples = syn.examples()

        if examples:
            print(f"   Usage example: {', '.join(examples)}")

        print()

def explore_hypernyms():
    """
    Display hypernyms (more general terms) for the first synset in the global synsets list.
    
    Hypernyms represent "is-a" relationships where the synset is a specific instance of its hypernyms.
    For example, "dog" has a hypernym "canine".
    """
    global synsets

    syn = synsets[0]
    print(f"\n=== Hypernyms for '{syn.name()}' ===")
    
    hypernyms = syn.hypernyms()

    if hypernyms:
        print("Hypernyms (more general terms):")

        for hyper in hypernyms:
            print(f"  - {hyper.name()}: {hyper.definition()}")
    else:
        print("No hypernyms found for this synset")
    
def explore_hyponyms():
    """
    Display hyponyms (more specific terms) for the first synset in the global synsets list.
    
    Hyponyms represent "is-a" relationships where the hyponym is a specific instance of the synset.
    For example, "dog" has hyponyms like "poodle" and "retriever".
    Limits output to first 5 hyponyms if there are many.
    """
    global synsets

    syn = synsets[0]
    print(f"\n=== Hyponyms for '{syn.name()}' ===")

    hyponyms = syn.hyponyms()

    if hyponyms:
        print("Hyponyms (more specific terms):")

        for hypo in hyponyms[:5]: 
            print(f"  - {hypo.name()}: {hypo.definition()}")

        if len(hyponyms) > 5:
            print(f"  ... and more {len(hyponyms) - 5} hyponyms")
    else:
        print("No hyponyms found for this synset")
    
def explore_meronyms(word):
    """
    Display part meronyms for the first synset of a given word.
    
    Meronyms represent "part-of" relationships where the meronym is a part of the synset.
    For example, "finger" is a meronym of "hand".
    
    Args:
        word (str): The word to explore meronyms for
    """
    global synsets

    if not synsets:
        print(f"No synsets found for '{word}'")
        return
    
    syn = synsets[0]
    print(f"\n=== Relations for '{syn.name()}' ===")

    part_meronyms = syn.part_meronyms()

    if part_meronyms:
        print("Meronyms (parts):")

        for part in part_meronyms:
            print(f"  - {part.name()}: {part.definition()}")

def explore_holonyms(word):
    """
    Display part holonyms for the first synset of a given word.
    
    Holonyms represent "has-a" relationships where the holonym contains the synset as a part.
    For example, "hand" is a holonym of "finger".
    
    Args:
        word (str): The word to explore holonyms for
    """
    global synsets
  
    if not synsets:
        print(f"No synsets found for '{word}'")
        return
    
    syn = synsets[0]
    print(f"\n=== Relation for '{syn.name()}' ===")

    part_holonyms = syn.part_holonyms()

    if part_holonyms:
        print("Holonyms (all):")

        for whole in part_holonyms:
            print(f"  - {whole.name()}: {whole.definition()}")

    else:
        print("No holonyms found for this synset")

def explore_antonyms(word):
    """
    Display antonyms for the first synset of a given word.
    
    Antonyms represent opposites of the word.
    For example, "hot" has an antonym "cold".
    
    Args:
        word (str): The word to explore antonyms for
    """
    global synsets
    
    if not synsets:
        print(f"No synsets found for '{word}'")
        return
    
    syn = synsets[0]
    print(f"\n=== Relations for'{syn.name()}' ===")

    antonyms = []

    for lemma in syn.lemmas():
        antonyms.extend(lemma.antonyms())
    
    if antonyms:
        print("Antonyms :")

        for ant in antonyms:
            ant_syn = ant.synset()
            print(f"  - {ant.name()}: {ant_syn.definition()}")

    else:
        print("No antonyms found for this synset")
    
def calculate_similarity(word1, word2):
    """
    Calculate and display semantic similarity measures between two words.
    Computes three similarity metrics:
    - Path similarity: Based on shortest path between synsets
       Formula: PathSim(s1, s2) = 1 / (1 + shortest_path_length(s1, s2))
       Where shortest_path_length is the minimum number of edges between synsets
    
    - Wu-Palmer similarity: Based on depth of synsets in the taxonomy
       Formula: WuPalmerSim(s1, s2) = (2 * depth(LCS)) / (depth(s1) + depth(s2))
       Where LCS is Least Common Subsumer (most specific common ancestor)
       and depth is the distance from the root node
    
    - Leacock-Chodorow similarity: Based on shortest path and taxonomy depth
       Formula: LCSim(s1, s2) = -log(shortest_path_length(s1, s2) / (2 * max_depth))
       Where max_depth is the maximum depth of the taxonomy
       Note: Only works for synsets with same part of speech
    
    Args:
        word1 (str): First word for comparison
        word2 (str): Second word for comparison
    """
    synsets1 = wn.synsets(word1)
    synsets2 = wn.synsets(word2)
    
    if not synsets1 or not synsets2:
        print(f"Could not find synsets for one or both words.")
        return
    
    syn1 = synsets1[0]
    syn2 = synsets2[0]
    
    print(f"\n=== Similarity between '{word1}' and '{word2}' ===")
    
    path_sim = syn1.path_similarity(syn2)
    print(f"Path similarity: {path_sim:.4f}")
    
    wup_sim = syn1.wup_similarity(syn2)

    if wup_sim is not None:
        print(f"Wu-Palmer similarity: {wup_sim:.4f}")
    else:
        print("Wu-Palmer similarity: Not available")
    
    try:
        lch_sim = syn1.lch_similarity(syn2)
        print(f"Leacock-Chodorow similarity: {lch_sim:.4f}")
    except:
        print("Leacock-Chodorow similarity: Not available for these synsets")

def add_hipernyms(syn, G, current_level=0, max_level=2):
    """
    Recursively add hypernyms to a directed graph up to a specified level.
    
    Args:
        syn (Synset): The synset to add hypernyms for
        G (DiGraph): The directed graph to add nodes and edges to
        current_level (int): The current level in the hierarchy
        max_level (int): The maximum level to traverse
    """
    if current_level >= max_level:
        return
        
    for hyper in syn.hypernyms():
        G.add_node(hyper.name())
        G.add_edge(syn.name(), hyper.name())
        add_hipernyms(hyper, G, current_level + 1, max_level)
     
def visualize_hierarchy(word, level=2):
    """
    Visualize the hypernym hierarchy for a given word as a directed graph.
    
    Creates a network graph showing the hypernym relationships (more general terms)
    for the given word up to the specified level in the hierarchy.
    
    Args:
        word (str): The word to visualize hierarchy for
        level (int, optional): How many levels up in the hierarchy to display. Defaults to 2.
    """
    synsets = wn.synsets(word)
    
    if not synsets:
        print(f"No synsets found for '{word}'")
        return
    
    root = synsets[0]
    
    G = nx.DiGraph()
    G.add_node(root.name())
        
    add_hipernyms(root, G, 0, level)
    
    plt.figure(figsize=(16, 12))

    pos = nx.kamada_kawai_layout(G)
    
    labels = {}

    for node in G.nodes(): 
        labels[node] = node.split('.')[0]
    
    node_size = 10000 
    
    nx.draw(G, pos, 
            node_color='lightblue',
            node_size=node_size, 
            arrows=True, 
            with_labels=False,  
            width=2) 
    
    for node, (x, y) in pos.items():
        plt.text(x, y, labels[node], 
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=12,  
                fontweight='bold',  
                color='black')
    
    plt.title(f"Hypernym Hierarchy for '{word}'", fontsize=16)
    plt.axis('off')
    
    plt.savefig(f"{word}_hierarchy.png", dpi=300, bbox_inches='tight')
    print(f"Hierarchy saved as '{word}_hierarchy.png'")

def main():
    """
    Main function to run the WordNet Explorer program.
    
    Provides a menu-driven interface for exploring various semantic relationships
    in WordNet for a given word. Options include exploring synonyms, hypernyms,
    hyponyms, meronyms, holonyms, antonyms, calculating similarity between words,
    and visualizing the hypernym hierarchy.
    """
    global synsets

    word = "default"
    synsets = new_synsets(word)

    running = True

    while running:
        print("\n=== WordNet Explorer ===")
        print("1. Explore Synonyms")
        print("2. Explore Hypernyms")
        print("3. Explore Hyponyms")
        print("4. Explore Meronyms")
        print("5. Explore Holonyms")
        print("6. Explore Antonyms")
        print("7. Calculate Similarity")
        print("8. Visualize Hierarchy")
        print("9. Change word")
        print("10. Exit")

        print(f"Current word: \033[91m{word}\033[0m")
        
        choice = input("Choose an option: ")
          
        match choice:
            case '1':
                explore_synonymous(word)
                input("Press Enter to continue...")

            case '2':
                explore_hypernyms()
                input("Press Enter to continue...")

            case '3':
                explore_hyponyms()
                input("Press Enter to continue...")

            case '4':
                explore_meronyms(word)
                input("Press Enter to continue...")

            case '5':
                explore_holonyms(word)
                input("Press Enter to continue...")

            case '6':
                explore_antonyms(word)
                input("Press Enter to continue...")

            case '7':
                word2 = input("Enter word to compare: ")
                calculate_similarity(word, word2)
                input("Press Enter to continue...")

            case '8':
                level = int(input("Enter the hierarchy level: "))
                visualize_hierarchy(word, level)
                input("Press Enter to continue...")

            case '9':
                word = input("Enter new word: ")
                synsets = new_synsets(word)

            case '10':
                running = False

            case _:
                print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()