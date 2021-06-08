import random
from datetime import datetime
from flask import request


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


def writeLogoView(cnx,fontFamilyId,fontWeightId,primaryColorId,ipAddress,requestTime):
    # Write logo view into logo_views table
    with cnx.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `logo_views` (`font_family_id`, `font_weight_id`, `primary_color_id`, `user_ip`,`created`) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (fontFamilyId, fontWeightId, primaryColorId, ipAddress, requestTime))
    # connection is not autocommit by default. So you must commit to save your changes.
    cnx.commit()


def getLogos(cnx,logosCount=3):
    logos = []
    for logo in range(logosCount):
        fontFamilyId, fontFamily = getFontFamily(cnx)
        fontWeightId, fontWeight = getFontWeight(cnx)
        primaryColorId, primaryColor = getPrimaryColor(cnx)
        logoAttributes = [{"Primary color": [primaryColorId, primaryColor]},
                          {"Font family": [fontFamilyId, fontFamily]},
                          {"Font weight": [fontWeightId, fontWeight]}]
        logos.append(logoAttributes)
        ipAddress = request.remote_addr
        requestTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writeLogoView(cnx, fontFamilyId, fontWeightId, primaryColorId, ipAddress, requestTime)
    return logos
