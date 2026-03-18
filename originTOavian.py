import re
from base64 import b64encode
#web imports:
from pyscript import when, display
from js import document
# base vowels:
vowels = ["a", "e", "i", "o"]
consonants = ["t", "k", "ʔ", "f", "s", "w", "l", "j", "m", "n", "ɾ", "r", "h"]
changes = []
output = ''
# base conditions:
gemination = False
vowellength = False
lowcoalesce = False
labiopalatalness = False
yvowel = False
loneglide = False
wrrd = ""

def orify(lst):  # makes it work like a|b|c|... for regex
    return '|'.join(map(re.escape, lst))

def lststr(lst):
    return ''.join(map(re.escape, lst))

def loopsub(pattern, result, txt):  # types like normal re.sub but loops to catch all cases
    while True:
        txt, nbr = re.subn(pattern, result, txt)
        if nbr == 0:
            return txt

def repair(txt):
    txt = loopsub(rf"([ː,ᶣ,ʲ,ʷ])\1+", "ː", txt)  # ːː > ː

    # vowel length
    txt = loopsub(rf"({vowels})\1+", r"\1ː", txt) if vowellength == True else loopsub(rf"({vowels})\1+", r"\1", txt)
    txt = loopsub(rf"({vowels})ˈ\1+", r"ˈ\1ː", txt) if vowellength == True else loopsub(rf"({vowels})ˈ\1+", r"ˈ\1", txt)
    # gemination
    txt = loopsub(rf"({orify(consonants)})\1+", r"\1ː", txt) if gemination == True else loopsub(rf"({orify(consonants)})\1+", r"\1", txt)
    txt = loopsub(rf"({orify(consonants)})ˈ\1+", r"\1ː", txt) if gemination == True else loopsub(rf"({orify(consonants)})ˈ\1+", r"ˈ\1", txt)
    txt = loopsub(rf"ɾː", r"r", txt) if gemination == True else loopsub(rf"ɾ(ˈ)?ɾ", r"\1r", txt)

    # lowcoalesce
    txt = loopsub(rf"oa|ao", "ɔː", txt) if lowcoalesce == True else txt
    txt = loopsub(rf"ea|ae", "ɛː", txt) if lowcoalesce == True else txt
    # labiopalatalness
    txt = loopsub(rf"ʲʷ|ᶣʷ|ʷᶣ|ʷʲ|ʲᶣ|ᶣʲ|ʲw|ᶣw|ʷɥ|ʷj|ʲɥ|ᶣj",rf"ᶣ",txt) if labiopalatalness == True else txt
    txt = loopsub(rf"(f|w|m|b|p)ᶣ", r"\1ʲ", txt) if labiopalatalness == True else txt
    txt = loopsub(rf"(ʃ|ʒ|tʃ|ʎ)ᶣ", r"\1ʷ", txt) if labiopalatalness == True else txt
    txt = loopsub(rf"(f|w|m|b|p)ʷ", r"\1", txt) if labiopalatalness == True else txt
    txt = loopsub(rf"(ʃ|ʒ|tʃ|ʎ)ʲ", r"\1", txt) if labiopalatalness == True else txt
    # glide repair
    txt = loopsub(rf"(?<!{vowels})(ɥ)(?={consonants})", r"y", txt) if yvowel == True and loneglide == True else txt
    txt = loopsub(rf"(?<!{vowels})(ᶣ)(?={consonants})", r"\1y", txt) if yvowel == True and loneglide == True else txt
    txt = loopsub(rf"(?<!{vowels})(j)(?={consonants})", r"i", txt) if loneglide == True else txt
    txt = loopsub(rf"(?<!{vowels})(ʲ)(?={consonants})", r"\1i", txt) if loneglide == True else txt
    txt = loopsub(rf"(?<!{vowels})(j)(?={consonants})", r"u", txt) if loneglide == True else txt
    txt = loopsub(rf"(?<!{vowels})(ʷ)(?={consonants})", r"\1u", txt) if loneglide == True else txt

    # fix stress
    txt = loopsub(rf"({consonants})(ː|ᶣ|ʲ|ʷ)?(ˈ)({vowels})", r"\3\1\2\4", txt)
    txt = loopsub(rf"({vowels})(ˈ)({consonants})({consonants})", r"\2\1\3\4", txt)
    txt = loopsub(rf"({consonants})(ˈ)(ᶣ|ʲ|ʷ)", r"\2\1\3", txt)
    txt = loopsub(rf"^({consonants})(ᶣ|ʲ|ʷ)?(ˈ)({consonants})", r"\3\1\2\4", txt)
    return txt

def stressify(txt):
    txt = txt.replace("ˈ", "-ˈ")
    txt = loopsub(rf"(?<={vowels})({orify(consonants)})({orify(consonants)})", r"\1-\2", txt)
    txt = loopsub(rf"({orify(vowels)}|ː)({orify(consonants)})(ᶣ|ʲ|ʷ)?(?=[^-])", r"\1-\2\3", txt)
    txt = loopsub(rf"({orify(vowels)})({orify(vowels)})", r"\1-\2", txt)
    lst = txt.split("-")
    happen=0
    while happen!=-1: #brute forcing all syllables to have a vowel and fit 2 cluster max
        for i in range(len(lst)):
            if not any(j in lst[i] for j in vowels):
                if i!=0:
                    lst[i-1]+=lst[i] # 'to', 'k' => 'tok'
                    del lst[i]
                    break
                else:
                    lst[i + 1] = lst[i]+lst[i + 1]  # 'f', 'to' => 'fto'
                    del lst[i]
                    break
            elif re.search(rf"^({consonants})(ᶣ|ʲ|ʷ)?(?=({consonants})(ᶣ|ʲ|ʷ)?({consonants}))", lst[i])!=None and i!=0:
                mch = re.search(rf"^({consonants})(ᶣ|ʲ|ʷ)?(?=({consonants})(ᶣ|ʲ|ʷ)?({consonants}))", lst[i]).group()
                if i != 0:
                    lst[i - 1] += mch  # 'to', 'k' => 'tok'
                    lst[i]=lst[i][len(mch):]
                    break
            elif i == len(lst)-1:
                happen=-1 #resolution only when ALL syllables have a vowel

    lst = [i for i in lst if i != ""]
    if "ˈ" not in txt:
        if "́" in txt:
            for i in range(len(lst)):
                if "́" in lst[i]:
                    lst[i] = "ˈ" + lst[i].replace("́", "")
        else:  # apply default penultimate stress
            if len(lst) >= 2:
                lst[-2] = "ˈ" + lst[-2].replace("́", "")
            else:
                lst[0] = "ˈ" + lst[0].replace("́", "")

    if len(lst) >= 4:  # if we need secondary stress
        for i in range(len(lst)):  # find the one with primary stress
            if "ˈ" in lst[i]:
                strsyl = i
                break
        for i in range(len(lst)):
            if strsyl % 2 == i % 2 and strsyl != i:
                lst[i] = "ˌ" + lst[i]

    for i in range(len(lst)):
        if "ˈ" in lst[i]:
            lst[i] = "ˈ"+lst[i].replace("ˈ","")
    return lst

@when("click","#evolve")
def main(event):
    # resetting stuff
    global vowels, consonants, changes
    changes = []
    vowels = ["a", "e", "i", "o"]
    consonants = ["t", "k", "ʔ", "f", "s", "w", "l", "j", "m", "n", "ɾ", "r", "h"]
    global gemination, vowellength, lowcoalesce, labiopalatalness, yvowel, loneglide
    gemination = False
    vowellength = False
    lowcoalesce = False
    labiopalatalness = False
    yvowel = False
    loneglide = False
    # get word
    """ this is for nonweb, in terminal
    passed = False
    while passed==False:
        X = input("word: ")
        if any(i in X for i in vowels):
            passed = True
        else:
            print("Every word has to have one of ORIGIN's vowels (a, i, e, o).")
            print("Please try again.")
    for web:"""
    passed = False
    wrrd = document.getElementById("wordin").value
    if any(i in wrrd for i in vowels):
        "a"
    else:
        print("Every word has to have one of ORIGIN's vowels (a, i, e, o).")
        print("Please try again.")
        return None
    for i in wrrd:
        if i not in vowels + consonants + ["y","́","̄","á","é","í","ó","ā","ē","ī","ō","'"]:
            print("You cannot use non-ORIGIN phonemes.")
            print("Please try again.")
            return None
    # make it ipa
    X = wrrd
    X = loopsub("á","á",X)
    X = loopsub("é","é",X)
    X = loopsub("í","í",X)
    X = loopsub("ó","ó",X)
    X = loopsub("ā","ā",X)
    X = loopsub("ē","ē",X)
    X = loopsub("ī","ī",X)
    X = loopsub("ō","ō",X)
    X = loopsub("kw|q", "kʷ", X)  # kw-ification
    X = X.replace("y", "j")  # yod
    X = X.replace("'", "ʔ").replace("‘","ʔ")  # glottal stop
    X = loopsub(rf"({orify(consonants)})\1+", r"\1ː", X)  # consonant gemination
    X = loopsub(rf"({vowels})\1+", r"\1ː", X)  # vowel length
    X = X.replace("̄", "ː")  # vowel length
    X = loopsub(rf"r(?=[^ː])", "ɾ", X)  # tapped r
    X = ''.join(map(re.escape, stressify(X))).replace("ˌ", "")
    # initial generals:
    gemination = True
    vowellength = True
    X = repair(X)
    pron = X

    # haplology
    # VCVC
    Y = X
    Y = loopsub(rf"({vowels})({orify(consonants)})\1\2$", r"\1\2ː\1", Y)  # / _#
    Y = loopsub(rf"({vowels})({orify(consonants)})\1\2", r"\1\2ː", Y)  # / !_#
    # CVCV
    Y = loopsub(rf"^({orify(consonants)})({vowels})\1\2", r"\2\1ː\2", Y)  # / #_
    Y = loopsub(rf"({orify(consonants)})({vowels})\1\2", r"\1ː\2", Y)  # / #_
    if Y != X:
        X = repair(Y)
        changes.append(f"1: Haplology | {X}")

    # glottal stop elision
    Y = X.replace("ʔ", "")
    consonants.remove("ʔ")
    if Y != X:
        X = repair(Y)
        changes.append(f"2: Glottal Stop Elision | {X}")

    # non-high vowel coalescence
    Y = X
    Y = loopsub(rf"o(ˈ)?a|a(ˈ)?o", r"\1ɔː", Y)
    Y = loopsub(rf"e(ˈ)?a|a(ˈ)?e", r"\1ɛː", Y)
    vowels.extend(["ɔ", "ɛ"])
    lowcoalesce = True
    if Y != X:
        X = repair(Y)
        changes.append(f"3: Non-High Vowel Coalescence | {X}")

    # short o raising
    Y = X
    Y = loopsub(rf"(?<!e)o(?=[^ːe]|$)", "u", Y)
    vowels.append("u")
    if Y != X:
        X = repair(Y)
        changes.append(f"4: Short O Raising | {X}")

    # high vowel synaeresis
    Y = X
    Y = loopsub(rf"(?<={vowels})u|u(?={vowels})","w",Y)
    Y = loopsub(rf"(?<={vowels})i(?!ː)|i(?!ː)(?={vowels})","j",Y)
    Y = loopsub(rf"({vowels})(ː)i",r"\1\2j",Y)
    Y = loopsub(rf"({vowels})(ː)u",r"\1\2w",Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"5: High Vowel Synaeresis | {X}")

    # h  divergence
    Y = X
    Y = loopsub(rf"hw", "f", Y)
    Y = loopsub(rf"hːw", "fː", Y)
    Y = loopsub(rf"hj", "ç", Y)
    Y = loopsub(rf"hːj", "çː", Y)
    Y = loopsub(rf"h(?=[uo])", "f", Y)
    Y = loopsub(rf"h(?=[i])", "ç", Y)
    Y = loopsub(rf"hː(?=[uo])", "fː", Y)
    Y = loopsub(rf"hː(?=[i])", "çː", Y)
    Y = loopsub(rf"h", "x", Y)
    consonants.extend(["ç", "x"])
    consonants.remove("h")
    if Y != X:
        X = repair(Y)
        changes.append(f"6: H Divergence | {X}")

    # middle vowel merger
    Y = X
    Y = loopsub("ɛ", "e", Y)
    Y = loopsub("ɔ", "o", Y)
    vowels.remove("ɛ")
    vowels.remove("ɔ")
    lowcoalesce = False
    if Y != X:
        X = repair(Y)
        changes.append(f"7: Middle Vowel merger | {X}")

    # high vowel monophthongization
    Y = X
    Y = loopsub("ij", "iː", Y)
    Y = loopsub("ji", "iː", Y)
    Y = loopsub("uw", "uː", Y)
    Y = loopsub("wu", "uː", Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"8: High Vowel Monophthongization | {X}")

    # palatalization
    Y = X
    Y = loopsub(rf"(?<={consonants})([ij])([^ː])?(ˈ)?", r"ʲ\2", Y)
    Y = loopsub(rf"(?<={consonants})iː", "ʲiː", Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"9: Palatalization | {X}")

    # unstressed low vowel reduction
    Y = stressify(X)
    if len(Y) == 1:  # if monosyllabic
        Y = Y
    else:
        for i in range(len(Y)):  # for each syllable
            if i == range(len(Y)) and "ˈ" not in Y[i]:  # if last syllable w/ no stress
                Y[i] = loopsub("a(?!ː)", "ə", Y[i])
            elif "ˈ" not in Y[i] and "ˌ" not in Y[i]:  # if syllable w/o any form of stress
                Y[i] = loopsub("a(?!ː)", "ə", Y[i])
    vowels.append('ə')
    Y = ''.join(map(re.escape, Y)).replace("ˌ", "")
    if Y != X:
        X = repair(Y)
        changes.append(f"10: Unstressed Low Vowel Reduction | {X}")

    # labiopalatal glide creation
    Y = X
    Y = loopsub(rf"(wj|jw|wʲ)", "ɥ", Y)
    Y = loopsub(rf"(ʲw|ʷj|ʷʲ)", "ᶣ", Y)
    Y = loopsub(rf"(ʲw|ʷj|ʷʲ)", "ᶣ", Y)
    Y = loopsub(rf"w(e|i)", r"ɥ\1", Y)
    Y = loopsub(rf"j(o|u)", r"ɥ\1", Y)
    Y = loopsub(rf"ʷ(e|i)", r"ᶣ\1", Y)
    Y = loopsub(rf"ʲ(o|u)", r"ᶣ\1", Y)
    consonants.append("ɥ")
    if Y != X:
        X = repair(Y)
        changes.append(f"11: Labiopalatal Glide Creation | {X}")

    # high front rounded vowel creation
    Y = X
    Y = loopsub(rf"(uj|ju|iw|ɥi|iɥ|ɥu|uɥ)", "y", Y)
    Y = loopsub(rf"^(ˈ)?ɥ(?=[^{vowels})", r"\1y", Y)
    Y = loopsub(rf"(?<!{orify(vowels)})ɥ$", r"y", Y)
    yvowel = True
    vowels.append("y")
    if Y != X:
        X = repair(Y)
        changes.append(f"12: High Front Rounded Vowel Creation | {X}")

    # labiopalatalization
    Y = X
    Y = loopsub(rf"({consonants})ɥ", r"\1ᶣ", Y)
    Y = loopsub(rf"({consonants})y", r"\1ᶣy", Y)
    labiopalatalness = True
    if Y != X:
        X = repair(Y)
        changes.append(f"13: Labiopalatalization | {X}")

    # mid-front rounded vowel creation
    Y = X
    Y = loopsub(rf"({consonants}ᶣ)(e|o)", r"\1ø", Y)
    Y = loopsub(rf"(ɥ)(e|o|ø)|(e|o|ø)(ɥ)", r"ø", Y)
    Y = loopsub(rf"(o|e|ø)(ː)?(ˈ)(o|e|ø)", r"\3øː", Y)
    vowels.append("ø")
    if Y != X:
        X = repair(Y)
        changes.append(f"14: Mid-front Rounded Vowel Creation | {X}")

    # labialization
    Y = X
    Y = loopsub(rf"({orify(consonants)}|ᶣ|ʲ|ʷ)(u|w)(?!ː)", r"\1ʷ", Y)
    Y = loopsub(rf"({orify(consonants)}|ᶣ|ʲ|ʷ)(uː)", r"\1ʷuː", Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"15: Labialization | {X}")

    # t affrication
    Y = X
    Y = loopsub("tʷ", "ʦ", Y)
    Y = loopsub("tᶣ", "ʦʲ", Y)
    consonants.append("ʦ")
    if Y != X:
        X = repair(Y)
        changes.append(f"16: T Affrication | {X}")

    ###LOSS OF gemination
    gemination = False

    # intervocalic ungeminated fricative voicing
    Y = loopsub(rf"({orify(vowels)}|w|j|ɥ)(ː)?(ˈ)?s(ᶣ|ʲ|ʷ)?({orify(vowels)}|w|j|ɥ)", r"\1\2\3z\4\5", Y) 
    Y = loopsub(rf"({orify(vowels)}|w|j|ɥ)(ː)?(ˈ)?f(ᶣ|ʲ|ʷ)?({orify(vowels)}|w|j|ɥ)", r"\1\2\3v\4\5", Y)
    Y = loopsub(rf"({orify(vowels)}|w|j|ɥ)(ː)?(ˈ)?x(ᶣ|ʲ|ʷ)?({orify(vowels)}|w|j|ɥ)", r"\1\2\3ɣ\4\5", Y)
    Y = loopsub(rf"({orify(vowels)}|w|j|ɥ)(ː)?(ˈ)?ç(ᶣ|ʲ|ʷ)?({orify(vowels)}|w|j|ɥ)", r"\1\2\3ʝ\4\5", Y)
    consonants.extend(["z", "v", "ɣ", "ʝ"])
    if Y != X:
        X = repair(Y)
        changes.append(f"17: Intervocalic Ungeminated Fricative Voicing | {X}")

    # geminate lateral palatalization
    Y = X
    Y = loopsub(rf"lː", "lʲ", Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"18: Geminate Lateral Palatalization | {X}")

    # de-gemination
    Y = X
    Y = loopsub(rf"({consonants})ː", r"\1", Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"19: De-gemination | {X}")

    ###
    # elision of initial y in hiatus
    Y = X
    Y = loopsub(rf"y({vowels})", r"ɥ\1", Y)
    Y = loopsub(rf"({vowels})ˈy", r"ˈ\1ɥ", Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"20: Elision of Initial /y/ in Hiatus | {X}")

    # schwa split
    Y = stressify(X)
    for i in range(len(Y)):
        if i == 0:
            Y[i] = loopsub(rf"^ə", "", Y[i])
        if i == len(Y):
            if "ˈ" not in Y[i]:
                Y[i] = loopsub(rf"ə$", "", Y[i])
        if "ˈ" not in Y[i] and "ˌ" not in Y[i]:
            Y[i] = loopsub(rf"({consonants})({consonants})ə(ˈ)?({consonants})", r"\1Q\2\3", Y[i])
            Y[i] = loopsub(rf"ə", "", Y[i])
        else:
            Y[i] = loopsub(rf"(m|w|f|v|ɥ|ᶣ|ʷ)ə|ə(m|w|f|v|ɥ)", r"\1ø\2", Y[i])
            Y[i] = loopsub(rf"ə", r"e", Y[i])
        if "Q" in Y[i]:
            Y[i]: loopsub(rf"Q", r"ə", Y[i])
            Y[i] = loopsub(rf"(m|w|f|v|ɥ|ᶣ|ʷ)ə|ə(m|w|f|v|ɥ)", r"\1ø\2", Y[i])
            Y[i] = loopsub(rf"ə", r"e", Y[i])
    Y = ''.join(map(re.escape, Y)).replace("ˌ", "")
    Y = loopsub(rf"({consonants})({consonants})(ˈ)?({consonants})",rf"\1ə\2\3\4",Y)
    Y = loopsub(rf"(m|w|f|v|ɥ|ᶣ|ʷ)ə|ə(m|w|f|v|ɥ)", r"\1ø\2", Y)
    Y = loopsub(rf"ə", r"e", Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"21: Schwa Split | {X}")

    # palatalization
    Y = X
    Y = loopsub(rf"(t|k)(ʲ|j)", "ʧ", Y)
    Y = loopsub(rf"s(ʲ|j)", "ʃ", Y)
    Y = loopsub(rf"z(ʲ|j)", "ʒ", Y)
    Y = loopsub(rf"ʦ(ʲ|j)", "ʧ", Y)
    Y = loopsub(rf"l(ʲ|j)", "ʎ", Y)
    Y = loopsub(rf"n(ʲ|j)", "ɲ", Y)
    Y = loopsub(rf"(t|k)ᶣ", "ʧʷ", Y)
    Y = loopsub(rf"sᶣ", "ʃʷ", Y)
    Y = loopsub(rf"zᶣ", "ʒʷ", Y)
    Y = loopsub(rf"ʦᶣ", "ʧʷ", Y)
    Y = loopsub(rf"lᶣ", "ʎʷ", Y)
    Y = loopsub(rf"nᶣ", "ɲʷ", Y)
    consonants.extend(["ʧ", "ʦ", "ʃ", "ʒ", "ʎ", "ɲ"])
    if Y != X:
        X = repair(Y)
        changes.append(f"22: Palatalization | {X}")

    # palatal fronting
    Y = loopsub(rf"ç", "ʃ", Y)
    Y = loopsub(rf"ʝ", "ʒ", Y)
    consonants.remove("ç") if "ç" in consonants else None
    consonants.remove("ʝ") if "ʝ" in consonants else None
    if Y != X:
        X = repair(Y)
        changes.append(f"23: Palatal Fronting | {X}")

    #non-sibilant fricative fortition
    Y = X
    Y = loopsub("f", "p", Y)
    Y = loopsub("v", "b", Y)
    Y = loopsub("x", "k", Y)
    Y = loopsub("ɣ", "g", Y)
    consonants.remove("f") if "f" in consonants else None
    consonants.remove("v") if "v" in consonants else None
    consonants.remove("x") if "x" in consonants else None
    consonants.remove("ɣ") if "ɣ" in consonants else None
    consonants.extend(["p", "b", "g"])
    if Y != X:
      X = repair(Y)
      changes.append(f"24: Non-Sibilant Fricative Fortition | {X}")

    # mid-high vowel-glide monophthongization
    Y = stressify(X)
    for i in range(len(Y)):  # this is to make sure i dont cross syl boundaries
      Y[i] = loopsub(r"ow|wo|ʷo(?!ː)", "u", Y[i])
      Y[i] = loopsub(r"ej|je", "i", Y[i])
    Y = ''.join(map(re.escape, Y)).replace("ˌ", "")
    if Y != X:
      X = repair(Y)
      changes.append(f"25: Mid-high Vowel-glide Monophthongization | {X}")

    #loss of vowel length distinction
    Y=X
    Y = loopsub(rf"({vowels})ː",r"\1",Y)
    vowellength = False
    if Y != X:
      X = repair(Y)
      changes.append(f"26: Vowel Length Loss of Distinction | {X}")

    #coarticulated liquid simplification
    Y=X
    Y = loopsub(rf"(ˈ)?([r,l,ɾ,ʎ])ʷ",r"\2uw\1",Y)
    Y = loopsub(rf"(ˈ)?([r,ɾ])ʲ",r"\2ij\1",Y)
    Y = loopsub(rf"(ˈ)?([r,l,ɾ])ᶣ",r"\2yɥ\1",Y)
    if Y != X:
      X = repair(Y)
      changes.append(f"27: Co-articulated Liquid Simplification | {X}")

    #lone glide vocalization
    Y=X
    Y = loopsub(rf"(?<!{vowels})w(?!{vowels})","u",Y)
    Y = loopsub(rf"(?<!{vowels})j(?!{vowels})","i",Y)
    Y = loopsub(rf"(?<!{vowels})ɥ(?!{vowels})","y",Y)
    loneglide = True
    Y=repair(Y)
    if Y != X:
      X = repair(Y)
      changes.append(f"28: Lone Glide Vocalization | {X}")

    #high vowel synaeresis
    Y=X
    Y = loopsub(rf"(?<={vowels})u|u(?={vowels})","w",Y)
    Y = loopsub(rf"(?<={vowels})i|i(?={vowels})","j",Y)
    Y = loopsub(rf"(?<={vowels})y|y(?={vowels})","ɥ",Y)
    if Y != X:
      X = repair(Y)
      changes.append(f"29: High Vowel Synaeresis | {X}")

    #glide absorption
    Y=X
    Y = loopsub(rf"(ʎ|j|ʃ|ʒ|ʧ|ɥ|ɲ)(ᶣ|ʲ)?j",r"\1\2",Y)
    Y = loopsub(rf"(ʎ|j|ʃ|ʒ|ʧ|ɥ|ɲ)(ᶣ|ʷ)?w", r"\1\2", Y)
    Y = loopsub(rf"(ʎ|j|ʃ|ʒ|ʧ|ɥ|ɲ)(ᶣ)?ɥ", r"\1\2", Y)
    if Y != X:
      X = repair(Y)
      changes.append(f"30: Glide Absorption | {X}")

    #liquid metathesis
    Y=X
    Y = loopsub(rf"({consonants})(l|r|ɾ|ʎ)(?!{vowels})",rf"\2\1",Y)
    if Y != X:
      X = repair(Y)
      changes.append(f"31: Liquid Metathesis | {X}")

    #labialized nasal fronting
    Y=X
    Y = loopsub("nʷ", "m",Y)
    Y = loopsub("ɲʷ","mʲ",Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"32: Labialized Nasal Fronting | {X}")

    #vowel hiatus resolution
    Y=X
    Y = loopsub(rf"(o|u)({vowels})|(o|u)({vowels})",rf"\1w\2",Y)
    Y = loopsub(rf"(ø|y)({vowels})|(ø|y)({vowels})", rf"\1ɥ\2", Y)
    Y = loopsub(rf"(e|i)({vowels})|(e|i)({vowels})", rf"\1j\2", Y)
    Y = loopsub(rf"(o|u)ˈ({vowels})|(o|u)ˈ({vowels})",rf"\1ˈw\2",Y)
    Y = loopsub(rf"(ø|y)ˈ({vowels})|(ø|y)ˈ({vowels})", rf"\1ˈɥ\2", Y)
    Y = loopsub(rf"(e|i)ˈ({vowels})|(e|i)ˈ({vowels})", rf"\1ˈj\2", Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"33: Vowel Hiatus Resolution | {X}")

    #sibilant whistling
    Y=X
    Y = loopsub(rf"(s|z|ʃ|ʒ|ʦ|ʧ)ʷ",r"\1͎",Y)
    if Y != X:
        X = repair(Y)
        changes.append(f"34: Sibilant Whistling | {X}")

    # re-orthographize
    Y=stressify(X)
    for i in range(len(Y)):
        if "ˈ" in Y[i]:
            if i != len(Y)-2 and len(Y) != 1:
                Y[i].replace("ˈ","")
                Y[i] = re.sub(rf"({vowels})",r"\1́",Y[i])
            break
    Y = ''.join(map(re.escape, Y)).replace("ˌ", "").replace("ˈ","").replace("uw","v").replace("ij","h")
    Z = Y
    be4 = ["v","ʷ|͎","ʲ","h","a","e","i","o","u","ø","y","p","b","t","ʦ","k","g","ʧ","s","z","ʃ","ʒ","r","ɾ","l","m","n","w","j","ɥ","ʎ","ɲ"]
    aft = ["уу","в","ь","ии","а","э","и","о","у","е","ю","п","б","т","ц","к","г","ч","с","з","ш","ж","р","д","л","м","н","ў","й","ы","ль","нь"]
    af2 = ["uu","v","́","ij","a","e","i","o","u","ø","y","p","b","t","ts","k","g","tś","s","z","ś","ź","r","d","l","m","n","w","j","ẃ","ł","ń"]
    for i in range(len(be4)):
        Y = re.sub(rf"({[be4[i]]})", rf"{aft[i]}",Y)
        Z = re.sub(rf"({[be4[i]]})", rf"{af2[i]}",Z)
    # final word
    document.getElementById("changelog").innerHTML = ""
    document.getElementById("changelog").innerHTML = '<br>'.join(map(re.escape,changes)).replace("\\","")
    document.getElementById("wordlist").innerHTML += f"<br>{wrrd} /{pron}/ => {Y} /{X}/ ({Z})"
    print(f"end: {X}")
    print(f"orth: {Y}")
    print(f"orth2: {Z}")
    print("- - - - - - - - -")
    return X, Y, Z
    
"""
def start():
    redo='y'
    toggle=False
    while redo.lower()!="n" and redo!="":
        main()
        if toggle == False:
            redo = input("again? (y/N): ")
            while redo.lower()!="n" and redo.lower()!="y" and redo!="":
                redo = input("wrong input,, (y/N): ")
        elif toggle == True:
            redo = input("again? (Y/n): ")
            if redo == "":
                redo = "y"
            while redo.lower()!="n" and redo.lower()!="y" and redo != "":
                redo = input("wrong input,, (Y/n): ")
        print("- - - - - - - - -")
        if redo == "Y":
            toggle = True
        # base vowels:
        global vowels, consonants
        vowels = ["a", "e", "i", "o"]
        consonants = ["t", "k", "ʔ", "f", "s", "w", "l", "j", "m", "n", "ɾ", "r", "h"]
        print(consonants)
        # base conditions:
        global gemination, vowellength, lowcoalesce, labiopalatalness, yvowel, loneglide
        gemination = False
        vowellength = False
        lowcoalesce = False
        labiopalatalness = False
        yvowel = False
        loneglide = False
    
    print("otena kō neya! | утэнакони́!")
"""
