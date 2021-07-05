import random
from flask import url_for
from connector import cloudSqlCnx
import numpy
from connector import cloudSqlCnx
import config
from datetime import datetime

cnx = cloudSqlCnx() # Open connection

def writeLogoView(brandName, brandArchetypeId, brandFieldId, fontFamilyId, fontWeightNum, textTransformId, primaryColorId, shapeId, ipAddress, requestTime):
    # Write logo view into logo_views table
    with cnx.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `logo_views` (`brand_name`,`brand_archetype_id`,`brand_field_id`,`font_family_id`, `font_weight_num`, `text_transform_id`, `primary_color_id`, `shape_id`, `user_ip`,`created`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (brandName,
                             brandArchetypeId,
                             brandFieldId,
                             fontFamilyId,
                             fontWeightNum,  # Not Id because weight value is countable (integer)
                             textTransformId,
                             primaryColorId,
                             shapeId,
                             ipAddress,
                             requestTime))
    # connection is not autocommit by default. So you must commit to save your changes.
    cnx.commit()


def writeLogoVote(brandName, brandArchetypeId, brandFieldId, fontFamilyId, fontWeightNum, textTransformId, primaryColorId, shapeId, ipAddress, requestTime):
    # Write logo vote into logo_views table
    with cnx.cursor() as cursor:
        # Create a new record
        sql = "INSERT INTO `logo_votes` (`brand_name`,`brand_archetype_id`,`brand_field_id`,`font_family_id`, `font_weight_num`, `text_transform_id`, `primary_color_id`, `shape_id`, `user_ip`,`created`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (brandName,
                             brandArchetypeId,
                             brandFieldId,
                             fontFamilyId,
                             fontWeightNum,  # Not Id because weight value is countable (integer)
                             textTransformId,
                             primaryColorId,
                             shapeId,
                             ipAddress,
                             requestTime))
    # connection is not autocommit by default. So you must commit to save your changes.
    cnx.commit()


def getMaxValues(colNames):
    maxValues = []
    for colName in colNames:
        with cnx.cursor() as cursor:
            # Asking for maximum id values
            sql = "SELECT MAX({value}) FROM logo_views".format(value=colName)
            cursor.execute(sql)
            maxValue = cursor.fetchall()[0][0]
            maxValues.append(maxValue)
    return maxValues


# Expanding data for Machine Learning / Each attribute value has its own index
def expandData(measurableValues, unmeasurableIds, unmeasurableMaxIds):
    fitDataExpanded = []
    # just add measurable parameters to the list
    fitDataExpanded.extend(measurableValues)
    # for unmeasurable attributes, a boolean parameter must be created for each possible id and set to 1 or 0
    for i in range(len(unmeasurableMaxIds)):
        for step in range(unmeasurableMaxIds[i]):
            if step == unmeasurableIds[i]:
                fitDataExpanded.append(1)
            else:
                fitDataExpanded.append(0)
    return fitDataExpanded


def getMlData(unmeasurableMaxIds):
    with cnx.cursor() as cursor:

        # Asking for grouped logo views
        cursor.execute('''
                SELECT COUNT(id), font_weight_num, brand_archetype_id, brand_field_id, font_family_id, primary_color_id, shape_id, text_transform_id
                FROM logo_views
                GROUP BY font_weight_num, brand_archetype_id, brand_field_id, font_family_id, primary_color_id, shape_id, text_transform_id
                ORDER BY COUNT(id) DESC;
                ''')
        logoViewsStats = cursor.fetchall()

        # Asking for grouped logo votes
        cursor.execute('''
                SELECT COUNT(id), font_weight_num, brand_archetype_id, brand_field_id, font_family_id, primary_color_id, shape_id, text_transform_id
                FROM logo_votes
                GROUP BY font_weight_num, brand_archetype_id, brand_field_id, font_family_id, primary_color_id, shape_id, text_transform_id
                ORDER BY COUNT(id) DESC;
                ''')
        logoVotesStats = cursor.fetchall()

        # Iterating threw views and votes, counting group likes
        mlAttributes = []
        mlFitness = []
        for viewGroup in range(len(logoViewsStats)):
            viewGroupLikes = 0
            viewsCount = logoViewsStats[viewGroup][0]
            viewsAttributes = logoViewsStats[viewGroup][1:] # crop after count

            #Counting likes number for every viewGroup
            for voteGroup in range(len(logoVotesStats)):
                votesCount = logoVotesStats[voteGroup][0]
                votesAttributes = logoVotesStats[voteGroup][1:] # crop after count
                if viewsAttributes == votesAttributes:
                    viewGroupLikes += votesCount

            # Calculating fitness
            fitness = viewGroupLikes / viewsCount
            mlFitness.append(fitness)

            # Expanding data for Machine Learning / Each attribute value has its own index
            measurableValues = [logoViewsStats[viewGroup][1]] # fontWeight
            unmeasurableIds = logoViewsStats[viewGroup][2:]
            expandedData = expandData(measurableValues, unmeasurableIds, unmeasurableMaxIds)
            mlAttributes.append(expandedData)

        return mlAttributes, mlFitness


def predictFitness(guessData):
    from sklearn.neighbors import KNeighborsRegressor
    maxValues = getMaxValues(config.unmeasurableRankingCols)
    modelData, modelFitness = getMlData(maxValues)

    # Data normalization
    from sklearn import preprocessing
    modelDataNormalized = preprocessing.minmax_scale(modelData)
    guessDataNormalized = preprocessing.minmax_scale(guessData)

    # Preparing regressor
    regressor = KNeighborsRegressor(n_neighbors = 10, weights = "distance")
    regressor.fit(modelDataNormalized, modelFitness)

    # asking for prediction for each logo, 1 logo == 1 guessData
    predictions = []
    for guessData in guessDataNormalized:
        npGuessData = numpy.array(guessData).reshape(1, -1) #converting numpy float64 to python float
        prediction = regressor.predict(npGuessData)[0]
        prediction = prediction.item()
        predictions.append(prediction)
    return predictions


def generateLogos(brandName, brandArchetype, businessCategories, countOfLogos, ipAddress, requestTime, previousLogo):
    startTime = datetime.now()

    # Loading all attributes from all tables in mysql
    allAttributes = {}
    allTables = config.measurableGraphicTbls + config.unmeasurableGraphicTbls
    for tableName in allTables:
        with cnx.cursor() as cursor:
            sql = "select * from {tableName}".format(tableName=tableName)
            cursor.execute(sql)
            allValues = cursor.fetchall()
            allAttributes[tableName] = allValues

    # Generating logos with selected brand parameters and random combination of attributes
    logos = []
    for logo in range(config.logoStorageSize):
        logo = {}
        logo['brand_name'] = brandName
        logo['brand_archetypes'] = brandArchetype
        logo['business_categories'] = businessCategories
        for attribute in allAttributes:
            rndValue = allAttributes[attribute][random.randint(0, len(allAttributes[attribute])-1)]
            logo[attribute] = rndValue
        logos.append(logo)

    # Preparing data for fitness prediction
    predictionInputs = []
    unmeasurableMaxIds = getMaxValues(config.unmeasurableRankingCols)
    for logo in logos:
        measurableValues = []
        unmeasurableIds = []
        for attribute in logo:
            # checking if attribute is measurable and sorting it into suitable list
            if type(logo[attribute][1]) == int:
                measurableValues.append(logo[attribute][1])
            else:
                unmeasurableIds.append(logo[attribute][0])
        predictionInput = expandData(measurableValues, unmeasurableIds, unmeasurableMaxIds)
        predictionInputs.append(predictionInput)

    # Calculating fitness prediction
    fitnessPredictions = predictFitness(predictionInputs)
    for i in range(len(logos)):
        logos[i]['fitness'] = fitnessPredictions[i]

    # Sorting by fitness
    def takeFitness(logo):
        return logo['fitness']
    logos.sort(key=takeFitness, reverse=True)

    # Selecting best logos (with highest fitness) from all logos
    bestLogos = logos[:countOfLogos]

    # Placement of previous logo into bestLogos
    # If it receives previous selected logo, it will replace one of the existing logos in bestLogos (depending on previousLogo order)
    if previousLogo != None:
        order = int(previousLogo['order'])
        bestLogos[order]['brand_name'] = previousLogo['brand_name']
        bestLogos[order]['brand_archetypes'] = (previousLogo['brand_archetypes_id'], previousLogo['brand_archetypes'])
        bestLogos[order]['business_categories'] = (previousLogo['business_categories_id'], previousLogo['business_categories'])
        bestLogos[order]['font_weights'] = (previousLogo['font_weights_id'], previousLogo['font_weights'])
        bestLogos[order]['font_families'] = (previousLogo['font_families_id'], previousLogo['font_families'])
        bestLogos[order]['primary_colors'] = (previousLogo['primary_colors_id'], previousLogo['primary_colors'])
        bestLogos[order]['shapes'] = (previousLogo['shapes_id'], previousLogo['shapes'])
        bestLogos[order]['text_transforms'] = (previousLogo['text_transforms_id'], previousLogo['text_transforms'])
        bestLogos[order]['fitness'] = 1.0 # Because user selected this logo
        bestLogos[order]['previous_logo'] = True  # adds information that it is previousLogo

    # Adding vote url
    order = 0
    for logo in bestLogos:
        logo['vote_url'] = url_for('get_logo_results',
                                   brand_name=logo['brand_name'],
                                   brand_archetypes_id=logo['brand_archetypes'][0],
                                   brand_archetypes=logo['brand_archetypes'][1],
                                   business_categories_id=logo['business_categories'][0],
                                   business_categories=logo['business_categories'][1],
                                   font_weights_id=logo['font_weights'][0],
                                   font_weights=logo['font_weights'][1],
                                   font_families_id=logo['font_families'][0],
                                   font_families=logo['font_families'][1],
                                   primary_colors_id=logo['primary_colors'][0],
                                   primary_colors=logo['primary_colors'][1],
                                   shapes_id=logo['shapes'][0],
                                   shapes=logo['shapes'][1],
                                   text_transforms_id=logo['text_transforms'][0],
                                   text_transforms=logo['text_transforms'][1],
                                   order=order, # Order in the list
                                   )
        order += 1

    # Adds best logos views to database
    for logo in bestLogos:
        writeLogoView(brandName,
                      logo['brand_archetypes'][0],
                      logo['business_categories'][0],
                      logo['font_families'][0],
                      logo['font_weights'][1],
                      logo['text_transforms'][0],
                      logo['primary_colors'][0],
                      logo['shapes'][0],
                      ipAddress,
                      requestTime)

    # Printing request duration
    requestDuration = datetime.now() - startTime
    print('{logosTotal} logos were generated and {logosSelected} best ones were selected in {requestDuration}'.format(logosTotal=config.logoStorageSize, logosSelected=countOfLogos, requestDuration=requestDuration))

    return bestLogos

