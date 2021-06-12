import random
from flask import request, url_for


def getFontFamily(cnx):
    with cnx.cursor() as cursor:
        cursor.execute('select * from font_families;')
        allFonts = cursor.fetchall()
        rndFontFamilyId = allFonts[random.randint(0, len(allFonts) - 1)][0]
        rndFontFamily = allFonts[random.randint(0, len(allFonts) - 1)][1]
    return rndFontFamilyId, rndFontFamily


def getFontWeight(cnx):
    with cnx.cursor() as cursor:
        cursor.execute('select * from font_weights;')
        allFontWeights = cursor.fetchall()
        rndFontWeightId = allFontWeights[random.randint(0, len(allFontWeights) - 1)][0]
        rndFontWeight = allFontWeights[random.randint(0, len(allFontWeights) - 1)][1]
    return rndFontWeightId, rndFontWeight


def getPrimaryColor(cnx):
    with cnx.cursor() as cursor:
        cursor.execute('select * from primary_colors;')
        allPrimaryColors = cursor.fetchall()
        rndPrimaryColorId = allPrimaryColors[random.randint(0, len(allPrimaryColors) - 1)][0]
        rndPrimaryColor = allPrimaryColors[random.randint(0, len(allPrimaryColors) - 1)][1]
    return rndPrimaryColorId, rndPrimaryColor

def getLogos(cnx,logosCount=3):
    logos = []
    for logo in range(logosCount):
        fontFamilyId, fontFamily = getFontFamily(cnx)
        fontWeightId, fontWeight = getFontWeight(cnx)
        primaryColorId, primaryColor = getPrimaryColor(cnx)
        voteUrl = url_for('get_logo_results',
                          fontFamily=fontFamilyId,
                          fontWeight=fontWeightId,
                          primaryColor=primaryColorId)
        logoAttributes = {"Vote url": voteUrl,
                          "Primary color": primaryColor,
                          "Primary color id": primaryColorId,
                          "Font family": fontFamily,
                          "Font family id": fontFamilyId,
                          "Font weight": fontWeight,
                          "Font weight id": fontWeightId,} # You can add attributes here
        logos.append(logoAttributes)
    return logos