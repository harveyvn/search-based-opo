package org.saarland.environmentanalyzer;

import org.saarland.accidentconstructor.AccidentConstructorUtil;
import org.saarland.accidentconstructor.ConsoleLogger;
import org.saarland.accidentelementmodel.NavigationDictionary;
import org.saarland.accidentelementmodel.Street;
import org.saarland.accidentelementmodel.TestCaseInfo;
import org.saarland.accidentelementmodel.VehicleAttr;
import org.saarland.nlptools.StanfordCoreferencer;
import org.saarland.nlptools.Stemmer;
import org.saarland.ontologyparser.AccidentConcept;
import org.saarland.ontologyparser.OntologyHandler;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;

public class RoadAnalyzer {

    ArrayList<Street> streetList;
    TestCaseInfo testCaseInfo;
    ArrayList<VehicleAttr> vehicleList;
    String[] tIntersectionNames = new String[] {"t-intersection", "t-junction", "three-legged", "merge"};
    String[] intersectionNames = new String[] {"intersection", "four-legged", "intersect"};
    OntologyHandler ontologyHandler;

    public RoadAnalyzer(ArrayList<Street> streetList,
                        OntologyHandler ontologyHandler,
                        TestCaseInfo testCase,
                        ArrayList<VehicleAttr> vehicleList)
    {
        this.streetList = streetList;
        this.ontologyHandler = ontologyHandler;
        this.vehicleList = vehicleList;
        testCaseInfo = testCase;
        //constructIntersectionNames();
    }

    /* ========================================================
     * ============== CREATE INTERSECTED ROADS ================
     * ========================================================
     */

    /*
     * Find whether a "T-intersection" or "intersection" is mentioned in a given paragraph
     */
    public String findIntersectionExistence(String paragraph)
    {
        String existJunctionType = "none";

        // Search T-intersection in the paragraph
        for (String tIntersectionType : tIntersectionNames)
        {
            // If this is an environment paragraph, just search for the intersection words
//            if (isEnvironmentParagraph)
//            {
                if (AccidentConstructorUtil.searchForWordInParagragh(tIntersectionType, paragraph))
                {
                    return "t-intersection";
                }
//            }
        }

        for (String intersectionType : intersectionNames)
        {
            // If this is an environment paragraph, just search for the intersection words
//            if (isEnvironmentParagraph)
//            {
                if (AccidentConstructorUtil.searchForWordInParagragh(intersectionType , paragraph))
                {
                    return "intersection";
                }
//            }
        }
        return "none";
    }


    /*
     * Create roads for junctions.
     *
     * If a T-intersection is found, create 2 streets with 1 street ends at the junction
     * If an intersection is found, create 2 streets crossing each other
     *
     */
    public void createEmptyRoads(String intersectionType, TestCaseInfo testCaseInfo)
    {
        testCaseInfo.createNewStreet();
        // Creates a crossing street
        Street secondStreet = testCaseInfo.createNewStreet();
        if (intersectionType.equals("t-intersection"))
        {
            secondStreet.putValToKey("is_single_road_piece", "T");
        }
    }

    /* ========================================================
     * ============== END CREATE INTERSECTED ROADS ============
     * ========================================================
     */

    // --------------------------------------------------------

    /* ========================================================
     * ============== IDENTIFY ROAD DIRECTION =================
     * ========================================================
     */
    public boolean analyzeRoadDirection(String intersectionType, String paragraph,
                                        StanfordCoreferencer stanfordCoreferencer)
    {
        // Search direction in format "[direction] [roadway concept word]"
        // Search direction in format "[direction] [lane]"
        identifyDirectionInRoads(paragraph, intersectionType, stanfordCoreferencer);

        return checkAllRoadHaveCardinalDirection();
    }

    /*
     *  Check if all the road has direction after analyzing this paragraph
     */

    public boolean checkAllRoadHaveCardinalDirection()
    {
        if (streetList.size() == 0)
        {
            return false;
        }
        for (Street street : streetList)
        {
            if (street.getStreetPropertyValue("road_navigation").equals(""))
            {
                return false;
            }
        }
        return true;
    }

    /*
     *  Find all the cardinal direction mentioned in the paragraph, then set them as direction of each junction
     */
    private void identifyDirectionInRoads(String paragraph, String intersectionType,
                                            StanfordCoreferencer stanfordCoreferencer)
    {
        String[] sentences = paragraph.split("\\. ");
        LinkedList<AccidentConcept> directionConcepts = ontologyHandler.getDirectionConcepts();
        LinkedList<AccidentConcept> roadConcepts = ontologyHandler.getRoadConcepts();

        for (String sentence : sentences)
        {
            ConsoleLogger.print('d', "Sentence:<BEGIN>" + sentence + "<END>");

            // Check if the direction is connected to a road
            LinkedList<LinkedList<String>> directionTaggedWordListAndDependency =
                    stanfordCoreferencer.findDependencies(sentence);

            LinkedList<String> sentenceDependencies = directionTaggedWordListAndDependency.get(1);

            // Check if any cardinal direction word is mentioned in the sentence
            boolean directionIsFound = false;
            for (AccidentConcept directionConcept : directionConcepts)
            {
                String directionName = directionConcept.getConceptName();

                ConsoleLogger.print('d', "Processing Direction " + directionName);

                // If there is a possible lane indicator, analyze this to discover the lane number

                if ( sentence.contains(" " + directionName + " ")
                    || sentence.contains(" " + directionName))
                {
                    directionIsFound = true;

                    String connectedDeps = AccidentConstructorUtil.findAllConnectedWordsTopDown(sentenceDependencies,
                            directionName, directionName,
                            0, 6);

                    ConsoleLogger.print('d', "Connected Direction Deps " + connectedDeps);

                    String[] relevantElements = connectedDeps.split(",");

                    Street assignedDirectionStreet = findRoadWithExistingDirection(directionName);

//                    // If the street direction is null, set it to a road with no cardinal direction
//                    if (assignedDirectionStreet == null)
//                    {
//                        if (streetList.size() > 0)
//                        {
//                            for (Street street : streetList)
//                            {
//                                if (street.getStreetPropertyValue("lane_num").equals("")) {
//                                    assignedDirectionStreet = street;
//                                    break;
//                                }
//                            }
//                        }
//                    } // End assign empty road direction to a temporary road



                    boolean isDirectionAssigned = false;

                    for (String elem : relevantElements)
                    {
                        String roadConceptName = AccidentConstructorUtil.getWordFromToken(elem);

                        // Find if a road is attached to this direction
                        AccidentConcept roadConcept = ontologyHandler.findExactConcept(roadConceptName);
//                        if ( (roadConcept != null && roadConcept.getLeafLevelName().equals("road_type"))
//                                || roadConceptName.equals("travel") || roadConceptName.startsWith("lane"))
//                        {
//
//                            if (roadConcept != null && roadConcept.getLeafLevelName().equals("road_type"))
//                            {
//                                ConsoleLogger.print('d', "Road concept group " + roadConcept.getLeafLevelName());
//                            }

                            ConsoleLogger.print('d', String.format("Find Direction Connection %s %s", directionName, roadConceptName));

                            if (assignedDirectionStreet == null)
                            {
                                assignedDirectionStreet = assignDirectionToRoad(directionName);
                                if (roadConcept != null && roadConcept.getLeafLevelName().equals("road_type"))
                                {
                                    assignedDirectionStreet.putValToKey("road_type", roadConceptName);
                                }

                                assignedDirectionStreet = findMainOrCrossingStreetInTJunction(sentenceDependencies, roadConceptName,
                                        assignedDirectionStreet);
                                isDirectionAssigned = true;
                            }

                            // If there is a possible lane indicator, analyze this to discover the lane number
                            if ( (connectedDeps.contains("lane") || connectedDeps.contains("-lane"))
                                    && (assignedDirectionStreet != null
                                    && assignedDirectionStreet.getStreetPropertyValue("lane_num").equals("")) )
                            {
                                ConsoleLogger.print('d', "Sentence contains lane indicator ");
                                int numberOfLanes = analyzeNumberOfLane(sentenceDependencies);
                                ConsoleLogger.print('d', "Number of Lanes is " + numberOfLanes
                                        + " street is null?" + (assignedDirectionStreet == null));
                                if (numberOfLanes > 0 && assignedDirectionStreet != null)
                                {
                                    assignedDirectionStreet.putValToKey("lane_num", numberOfLanes + "");
                                }
                            }

                            if (isDirectionAssigned)
                            {
                                break;
                            }

//                        } // End processing road concepts
                    } // End looping through connected words

                } // End checking if sentence contains the direction
            } // End looping through direction concepts

            if ( !directionIsFound && (sentence.contains(" lane") || sentence.contains("-lane")) )
            {
                ConsoleLogger.print('d', "Sentence contains lane indicator but direction not found");
                int numberOfLanes = analyzeNumberOfLane(sentenceDependencies);
                Street assignedDirectionStreet = null;

                if (streetList.size() > 0) {
                    if (streetList.get(0).getStreetPropertyValue("lane_num").equals(""))
                    {
                        assignedDirectionStreet = streetList.get(0);
                    }
                }
                else
                {
                    assignedDirectionStreet = testCaseInfo.createNewStreet();
                }


                ConsoleLogger.print('d', "Number of Lanes is " + numberOfLanes + " street is null?" + (assignedDirectionStreet == null));
                if (numberOfLanes > 0)
                {
                    if (assignedDirectionStreet != null)
                    {
                        ConsoleLogger.print('d', "Assign lane number to UNKNOWN existing road");
                        assignedDirectionStreet.putValToKey("lane_num", numberOfLanes + "");
                    }
                }
            }

        } // End looping through sentences
    }

    /*
     *  Update the direction to existing road, or create a new one if there is no road with the given direction.
     *  @return a road being assigned with the given direction
     */
    private Street assignDirectionToRoad(String direction)
    {
        // If no road is created, make a new one
        String directionCode = AccidentConstructorUtil.convertDirectionWordToDirectionLetter(direction);
        if (streetList.size() == 0)
        {
            Street newStreet = testCaseInfo.createNewStreet();

            newStreet.putValToKey("road_navigation", directionCode);

            return newStreet;
        }
        // Assign direction to existing road, if the road does not have a matching or same axis direction, make a new one
        else
        {
            int validStreetIndex = -1;
            for (int i = 0; i < streetList.size(); i++)
            {
                Street currentStreet = streetList.get(i);
                // If the street is empty, set the direction to this street.
                ConsoleLogger.print('d', "Road navigation before assign is empty? " + currentStreet.getStreetPropertyValue("road_navigation").equals(""));

                if ( currentStreet.getStreetPropertyValue("road_navigation").equals("") )
                {
                    ConsoleLogger.print('d', "Valid street found!");

                    validStreetIndex = i;
                    currentStreet.putValToKey("road_navigation", directionCode);
                    return currentStreet;
                }
            } // End looping through streets

            // If no road has an updatable cardinal direction, make a new road and assign the direction value to it
            if (validStreetIndex == -1)
            {
                ConsoleLogger.print('d', "No street with valid road_navigation slot found, create new one");
                Street newStreet = testCaseInfo.createNewStreet();
                newStreet.putValToKey("road_navigation", directionCode);
                return newStreet;
            }

        }
        return null;
    }

    private Street findMainOrCrossingStreetInTJunction(LinkedList<String> dependencyList, String roadName,
                                                     Street chosenStreet)
    {
        // If this is a T-intersection, attempt to find the main / crossing streets
        String relatedRoadProps = AccidentConstructorUtil.findAllConnectedWordsTopDown(dependencyList,
                roadName, "", 0, 2);

        AccidentConcept roadConcept = ontologyHandler.findExactConcept(roadName);

        // If the road type indicates the road ends at the intersection, set the road as the crossing street.
        if (roadConcept != null && roadConcept.getDataProperties() != null
                && roadConcept.getDataProperties().get("is_single_road_piece") != null)
        {
            if (roadConcept.getDataProperties().get("is_single_road_piece").equals("1"))
            {
                chosenStreet.putValToKey("is_single_road_piece", "T");
                return chosenStreet;
            }
        }
        else
        {
            // Find main/crossing indicators
            for (String property : relatedRoadProps.split(",")) {
                // This is a main street road
                if (property.startsWith("main-")) {
                    chosenStreet.putValToKey("is_single_road_piece", "F");
                    ConsoleLogger.print('d', "Main street found with direction "
                            + chosenStreet.getStreetPropertyValue("road_navigation"));
                    return chosenStreet;
                } else if (property.contains("cross") || property.startsWith("end")) {
                    chosenStreet.putValToKey("is_single_road_piece", "T");

                    ConsoleLogger.print('d', "Crossing street found with direction "
                            + chosenStreet.getStreetPropertyValue("road_navigation"));

                    return chosenStreet;
                }
            } // End looping through connected words
        } // End processing other road types
        return null;
    }

    /*
     *  Find if there is a street object with the same direction, or has direction of the same axis
     */
    private Street findRoadWithExistingDirection(String direction)
    {
        String directionCode = AccidentConstructorUtil.convertDirectionWordToDirectionLetter(direction);
        for (Street street : streetList)
        {
            String streetDirection = street.getStreetPropertyValue("road_navigation");
            if (streetDirection.equals(directionCode)
                || NavigationDictionary.isDirectionsInSameAxis(streetDirection, directionCode))
            {
                return street;
            }
        }
        return null;
    }

    /* ========================================================
     * =========== END ROAD DIRECTION IDENTIFICATION ==========
     * ========================================================
     */

    // --------------------------------------------------------

    /* ========================================================
     * =============== IDENTIFY ROAD BY TYPE  =================
     * ========================================================
     */

    /*
     * Create road objects by finding the type of the road in a paragraph. This function is called when 1) an intersection
     * is found, but there are less than 2 road objects being created 2) There is no road object being created after
     * searching the existence of intersection or road directions
     */
    public void constructRoadByRoadType(String paragraph)
    {
        ConsoleLogger.print('d', "Identify Road By Type");
        String[] sentences = paragraph.split("\\. ");

        for (String sentence : sentences) {
            ConsoleLogger.print('d', "Sentence:<BEGIN>" + sentence + "<END>");
            // Check if any cardinal direction word is mentioned in the sentence
            String[] wordsInSentence = sentence.split(" ");

            for (String word : wordsInSentence)
            {
                AccidentConcept wordConcept = ontologyHandler.findExactConcept(word);

                if (wordConcept != null && wordConcept.getLeafLevelName().equals("road_type"))
                {
                    ConsoleLogger.print('d', "Found road type concept");

                    if (streetList.size() == 0)
                    {
                        Street newStreet = testCaseInfo.createNewStreet();
                        newStreet.putValToKey("road_type", word);
                    }
                    else
                    {
                        // Scan the road object to see if this road type is already recorded
                        for (Street street : streetList)
                        {
                            if (street.getStreetPropertyValue("road_type").equals(word))
                            {
                                break;
                            }
                        }

                        // If this point is reached, there is no road segment with the same road type, make a new one
                        if (streetList.size() < 2)
                        {
                            Street newStreet = testCaseInfo.createNewStreet();
                            newStreet.putValToKey("road_type", word);
                        }
                    } // End processing non-empty street list

                }

            } // End checking each word

        } // End looping through sentences
    }

    /* ========================================================
     * =========== END ROAD TYPE IDENTIFICATION ===============
     * ========================================================
     */


    // --------------------------------------------------------

    /* ========================================================
     * =============== IDENTIFY PARKING SPACE =================
     * ========================================================
     */

    public void identifyParkingSetup(LinkedList<String> dependencyList, String paragraph)
    {
        // Check if we find any park in this paragraph
        if (!paragraph.contains("park")) {
            return;
        }
        HashMap<String, String> newTestCaseProp = testCaseInfo.getTestCaseProp();
        String connectedWordList = AccidentConstructorUtil.
            findAllConnectedWordsTopDown(dependencyList, "park", "", 0, 5);
        ConsoleLogger.print('d', "Environment park found " + connectedWordList);
        Street parkedStreet = null;

        if (testCaseInfo.getStreetList().size() == 1) {
            parkedStreet = testCaseInfo.getStreetList().get(0);
        }
        // Find vehicle ID first
        if (connectedWordList.matches(".*vehicle\\d.*")) {
            ConsoleLogger.print('d', "A parked vehicle found");
        } else  // if a vehicle with ID cannot be found, check which vehicle is identified as park
        {
            ConsoleLogger.print('d', "Cannot find a parked vehicleID");

            for (VehicleAttr vehicleTemp : vehicleList) {
                ConsoleLogger.print('d', "Onstreet of vehicle " + vehicleTemp.getVehicleId() + " is " + vehicleTemp.getOnStreet());
                if (vehicleTemp.getOnStreet() != 1) {
                    vehicleTemp.setTravelOnLaneNumber(AccidentConstructorUtil.detectTravellingLane(connectedWordList));

                    ConsoleLogger.print('d', "Environment parked vehicle #" + vehicleTemp.getVehicleId() +
                        " at lane number " + vehicleTemp.getTravelOnLaneNumber());

                    // Since this vehicle parked on a lane, it is set to locate on the street instead of
                    // a pavement
                    vehicleTemp.setOnStreet(1);
                }
            }
        }


        // Extract Misc descriptions
        for (String dependency : dependencyList) {
            String[] tokenPair = AccidentConstructorUtil.getWordPairFromDependency(dependency);

            String[] wordPair = {
                AccidentConstructorUtil.getWordFromToken(tokenPair[0]),
                AccidentConstructorUtil.getWordFromToken(tokenPair[1])
            };

            if (dependency.startsWith("nmod:of")) {

                for (String word : wordPair) {
                    AccidentConcept wordConcept = ontologyHandler.findExactConcept(word);
                    // Find whether street has parking line
                    if (wordConcept != null
                        && wordConcept.getLeafLevelName().equals("road_type")
                        && dependency.contains("side-")) {

                        String sidePattern = "side";

                        String relatedSideString = AccidentConstructorUtil
                            .findAllConnectedWordsTopDown(dependencyList, "side", "", 0, 1);
                        //                    String sidePattern = "side-";
                        //                    LinkedList<String> relatedSideDependencies = AccidentConstructorUtil.findConnectedDependencies(dependencyList, taggedWordList,
                        //                        sidePattern, dependency, 0);

                        ConsoleLogger.print('d', "relatedSideString = " +
                            relatedSideString);

                        // Check indicator of parked cars
                        if (relatedSideString.contains(",line") || relatedSideString.contains(",fill") ) {
                            String carLineDeps = AccidentConstructorUtil
                                .findAllConnectedWordsTopDown(dependencyList, "line", "", 0, 2);
                            ConsoleLogger.print('d', "carLineDeps = " +
                                carLineDeps);

                            if (carLineDeps.contains(",car")) {
                                parkedStreet.putValToKey("road_park_line_fill", "1");

                                ConsoleLogger.print('d', "find line filled with cars");

                                // If the parking line is not found yet, set both sides have a parking line
                                if (parkedStreet.getStreetPropertyValue("road_park_line").equals("")) {
                                    parkedStreet.putValToKey("road_park_line", "3");
                                }

                                if (relatedSideString.contains(",right-")
                                    && ( parkedStreet.getStreetPropertyValue("road_park_line").equals("")
                                        || parkedStreet.getStreetPropertyValue("road_park_line").equals("3"))) {

                                    parkedStreet.putValToKey("road_park_line", "2");

                                } else if (relatedSideString.contains(",left-")
                                    && ( parkedStreet.getStreetPropertyValue("road_park_line").equals("")
                                        || parkedStreet.getStreetPropertyValue("road_park_line").equals("3"))) {

                                    parkedStreet.putValToKey("road_park_line", "1");
                                }
                            }
                        }
                    }
                }

                    // Check if side dependency has line for parking
//                    for (String sideDependency : relatedSideDependencies) {
//                        ConsoleLogger.print('d', "Side related Dep " + sideDependency);
//                        String[] sideDepWordPair = AccidentConstructorUtil.getWordPairFromDependency(sideDependency);
//
//                        String otherWord = AccidentConstructorUtil.getOtherWordInDep(sidePattern, sideDepWordPair);
//
//                        // Check if the parking line is filled with cars
//                        if (otherWord.contains("line")) {
//                            LinkedList<String> carLineDeps = AccidentConstructorUtil.findConnectedDependencies(
////                                dependencyList, taggedWordList,
////                                otherWord, sideDependency, 0);
//                            ConsoleLogger.print('d', "Other word " + otherWord + " Car line Deps size " + carLineDeps.size());
                            // No info about the objects on the parking line
//                            if (carLineDeps.size() == 0) {
//        //                                    newTestCaseProp.put("road_park_line_fill", "0");
//                                parkedStreet.putValToKey("road_park_line_fill", "0");
//                            }
//
//                            for (String carDependency : carLineDeps) {
//                                // Found that the line is filled with cars
//                                if (carDependency.contains("car")) {
//                                    ConsoleLogger.print('d', "find line filled with cars");
//        //                                        newTestCaseProp.put("road_park_line_fill", "1");
//                                    parkedStreet.putValToKey("road_park_line_fill", "1");
//
//                                    // If the parking line is not found yet, set both sides have a parking line
//                                    if (newTestCaseProp.get("road_park_line").equals("")) {
//        //                                            newTestCaseProp.put("road_park_line", "3");
//                                        parkedStreet.putValToKey("road_park_line", "3");
//                                    }
//                                }
//                            }
//                        } // End checking if parking line is filled with cars
                        // Detect left parking line
//                        else if (otherWord.contains("(left-")) {
//                            if (newTestCaseProp.get("road_park_line").equals("")
//                                || newTestCaseProp.get("road_park_line").equals("3")) {
//        //                                    newTestCaseProp.put("road_park_line", "1");
//                                parkedStreet.putValToKey("road_park_line", "1");
//                            }
//                            // If somehow people specify "left and right", the set the lane has both parking lines
//                            else if (newTestCaseProp.get("road_park_line").equals("2")) {
//        //                                    newTestCaseProp.put("road_park_line", "3");
//                                parkedStreet.putValToKey("road_park_line", "3");
//                            }
//
//                        }
//                        // Detect right parking line
//                        else if (otherWord.contains("(right-")) {
//                            if (newTestCaseProp.get("road_park_line").equals("")
//                                || newTestCaseProp.get("road_park_line").equals("3")) {
//        //                                    newTestCaseProp.put("road_park_line", "2");
//                                parkedStreet.putValToKey("road_park_line", "2");
//                            }
//                            // If somehow people specify "left and right", the set the lane has both parking lines
//                            else if (newTestCaseProp.get("road_park_line").equals("1")) {
//        //                                    newTestCaseProp.put("road_park_line", "3");
//                                parkedStreet.putValToKey("road_park_line", "3");
//                            }
//                        }

                    } // End processing line dependency
                } // End checking road has parking line
                if (parkedStreet.getStreetProp() != null) {
                    parkedStreet.printStreetInfo();
//                    parkedStreet.setStreetProp(parkedStreetProp);
                }
//            }
//        }
    }

    /* ========================================================
     * =========== END PARKING SPACE IDENTIFICATION ===========
     * ========================================================
     */

    /* ========================================================
     * =============== IDENTIFY NUMBER OF LANE=================
     * ========================================================
     */
    /*
     * Analyze the lane number from the dependency list
     */
    public int analyzeNumberOfLane(LinkedList<String> dependencyList) {

        int numberOfLanes = 0;
        for (String dependency : dependencyList)
        {
            String[] wordPair = AccidentConstructorUtil.getWordPairFromDependency(dependency);
            for (String laneWord : wordPair)
            {
                laneWord = AccidentConstructorUtil.getWordFromToken(laneWord);
                ConsoleLogger.print('d', "laneWord is " + laneWord);
                if (laneWord.matches("\\d-lane"))
                {
                    numberOfLanes = Integer.parseInt(laneWord.split("-")[0]);
                    ConsoleLogger.print('d', "Find specific lane number " + numberOfLanes);
                }
                else if (laneWord.startsWith("lane"))
                {
                    String laneRelatedDeps = AccidentConstructorUtil.findAllConnectedWordsTopDown(dependencyList, laneWord, "", 0, 1);
                    String[] wordList = laneRelatedDeps.split(",");
                    ConsoleLogger.print('d', "related deps for lane analysis of roadType: " + laneWord + " is \n "
                            + laneRelatedDeps);
                    for (String word : wordList) {
                        String wordToken = AccidentConstructorUtil.getWordFromToken(word);

                        if (AccidentConstructorUtil.isNumeric(wordToken)) {
                            ConsoleLogger.print('d', "Numeric lane number " + wordToken);
                            numberOfLanes = (int)Double.parseDouble(wordToken);
                        }
                    }
                }
            }
        }
        return numberOfLanes;
    }
    /* ========================================================
     * =============== END IDENTIFY NUMBER OF LANE ============
     * ========================================================
     */
//    private void constructIntersectionNames() {
//        LinkedList<AccidentConcept> intersectionConcept = ontologyHandler.getDirectionConcepts();
//
//        intersectionNames = new ArrayList<String>();
//
//        // Collect all the names of intersection types
//        for (AccidentConcept concept : intersectionConcept)
//        {
//            intersectionNames.add(concept.getConceptName());
//        }
//
//        intersectionNames.add("intersect");
//
//        ConsoleLogger.print('d', "Intersection Names are " + intersectionNames.toString());
//    }

}
