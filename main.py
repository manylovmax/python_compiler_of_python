from lexical_analyzer import LexicalAnalyzer

# la = LexicalAnalyzer('hello_world.py')
la = LexicalAnalyzer('variables.py')
# la = LexicalAnalyzer('if.py')
la.analyze()
