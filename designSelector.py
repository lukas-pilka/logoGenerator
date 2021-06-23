import random
from flask import request, url_for
from connector import cloudSqlCnx
import numpy

# Expanding data for Machine Learning / Each attribute value has its own index
def expandData(fitData,maxValues):
    fitDataExpanded = []
    for i in range(len(maxValues)):
        for step in range(maxValues[i]):
            if step == fitData[i]:
                fitDataExpanded.append(1)
            else:
                fitDataExpanded.append(0)
    return fitDataExpanded

def getMaxValues(cnx):
    with cnx.cursor() as cursor:

        # Asking for maximum id values
        cursor.execute('''
                SELECT MAX(brand_archetype_id), MAX(brand_field_id), MAX(font_family_id), MAX(font_weight_id), MAX(primary_color_id)
                FROM logo_views
                ''')
        maxValues = list(cursor.fetchall()[0])
        return maxValues

def getMlData(cnx, maxValues):
    with cnx.cursor() as cursor:

        # Asking for grouped logo views
        cursor.execute('''
                SELECT COUNT(id), brand_archetype_id, brand_field_id, font_family_id, font_weight_id, primary_color_id
                FROM logo_views
                GROUP BY brand_archetype_id, brand_field_id, font_family_id, font_weight_id, primary_color_id
                ORDER BY COUNT(id) DESC;
                ''')
        logoViewsStats = cursor.fetchall()

        # Asking for grouped logo votes
        cursor.execute('''
                SELECT COUNT(id), brand_archetype_id, brand_field_id, font_family_id, font_weight_id, primary_color_id
                FROM logo_votes
                GROUP BY brand_archetype_id, brand_field_id, font_family_id, font_weight_id, primary_color_id
                ORDER BY COUNT(id) DESC;
                ''')
        logoVotesStats = cursor.fetchall()

        # Iterating threw views and votes, counting group likes
        mlAttributes = []
        mlFitness = []
        for viewGroup in range(len(logoViewsStats)):
            viewGroupLikes = 0
            viewsCount = logoViewsStats[viewGroup][0]
            viewsAttributes = logoViewsStats[viewGroup][1:]

            #Counting likes number for every viewGroup
            for voteGroup in range(len(logoVotesStats)):
                votesCount = logoVotesStats[voteGroup][0]
                votesAttributes = logoVotesStats[voteGroup][1:]
                if viewsAttributes == votesAttributes:
                    viewGroupLikes += votesCount

            # Calculating fitness
            fitness = viewGroupLikes / viewsCount
            mlFitness.append(fitness)

            # Expanding data for Machine Learning / Each attribute value has its own index
            expandedData = expandData(list(viewsAttributes), maxValues)
            mlAttributes.append(expandedData)

        return mlAttributes, mlFitness

def predictFitness(guessData):
    cnx = cloudSqlCnx() # Open connection
    maxValues = getMaxValues(cnx)
    mlAttributes, mlFitness = getMlData(cnx, maxValues)
    from sklearn.neighbors import KNeighborsRegressor
    regressor = KNeighborsRegressor(n_neighbors = 10, weights = "distance")
    regressor.fit(mlAttributes, mlFitness)

    # numpy reshaping is necessary because it is a single guess prediction
    npGuessData = numpy.array([guessData]).reshape(1, -1)
    prediction = regressor.predict(npGuessData)
    return prediction


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


def getTextTransform(cnx):
    with cnx.cursor() as cursor:
        cursor.execute('select * from text_transforms;')
        allTextTransforms = cursor.fetchall()
        rndTextTransformId = allTextTransforms[random.randint(0, len(allTextTransforms) - 1)][0]
        rndTextTransform = allTextTransforms[random.randint(0, len(allTextTransforms) - 1)][1]
    return rndTextTransformId, rndTextTransform


def getShape(cnx):
    with cnx.cursor() as cursor:
        cursor.execute('select * from shapes;')
        allShapes = cursor.fetchall()
        rndShapeId = allShapes[random.randint(0, len(allShapes) - 1)][0]
        rndShape = allShapes[random.randint(0, len(allShapes) - 1)][1]
    return rndShapeId, rndShape


def writeLogoView(cnx,fontFamilyId,fontWeightId,primaryColorId,ipAddress,requestTime):
    # Write logo view into logo_views table
    with cnx.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `logo_views` (`font_family_id`, `font_weight_id`, `primary_color_id`, `user_ip`,`created`) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (fontFamilyId, fontWeightId, primaryColorId, ipAddress, requestTime))
    # connection is not autocommit by default. So you must commit to save your changes.
    cnx.commit()


def getLogos(cnx, brandName, brandArchetypeId, brandFieldId, logosCount=3):
    logos = []
    for logo in range(logosCount):
        fontFamilyId, fontFamily = getFontFamily(cnx)
        fontWeightId, fontWeight = getFontWeight(cnx)
        textTransformId, textTransform = getTextTransform(cnx)
        primaryColorId, primaryColor = getPrimaryColor(cnx)
        shapeId, shape = getShape(cnx)

        # Preparing data for fitness prediction
        maxValues = getMaxValues(cnx)
        fitData = [brandArchetypeId, brandFieldId, fontFamilyId, fontWeightId, primaryColorId]
        guessData = expandData(fitData, maxValues)
        fitnessPrediction = predictFitness(guessData)

        # You can add attributes here
        voteUrl = url_for('get_logo_results',
                          brandName=brandName,
                          brandArchetype=brandArchetypeId,
                          brandField=brandFieldId,
                          fontFamily=fontFamilyId,
                          fontWeight=fontWeightId,
                          primaryColor=primaryColorId)
        logoAttributes = {"Vote url": voteUrl,
                          "Brand name": brandName,
                          "Primary color": primaryColor,
                          "Primary color id": primaryColorId,
                          "Font family": fontFamily,
                          "Font family id": fontFamilyId,
                          "Font weight": fontWeight,
                          "Font weight id": fontWeightId,
                          "Text transform": textTransform,
                          "Text transform id": textTransformId,
                          "Shape": shape,
                          "Shape id": shapeId,
                          "Fitness prediction": fitnessPrediction,}  # You can add attributes here
        logos.append(logoAttributes)
    return logos
