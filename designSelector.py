import random

def getFontFamily(cnx):
    with cnx.cursor() as cursor:
        cursor.execute('select * from font_families;')
        allFonts = cursor.fetchall()
        rndFontFamilyId = allFonts[random.randint(0, len(allFonts) - 1)][0]
        rndFontFamily = allFonts[random.randint(0, len(allFonts)-1)][1]
    return rndFontFamilyId, rndFontFamily

def getFontWeight(cnx):
    with cnx.cursor() as cursor:
        cursor.execute('select * from font_weights;')
        allFontWeights = cursor.fetchall()
        rndFontWeightId = allFontWeights[random.randint(0, len(allFontWeights) - 1)][0]
        rndFontWeight = allFontWeights[random.randint(0, len(allFontWeights)-1)][1]
    return rndFontWeightId, rndFontWeight