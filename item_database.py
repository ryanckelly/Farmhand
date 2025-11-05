"""
Comprehensive Stardew Valley Item Database

This module provides item ID to name mapping, categories, sources, and acquisition guides.
Data is based on game files and Stardew Valley Wiki.

Item IDs reference: https://stardewvalleywiki.com/Modding:Object_data
"""

# Quality levels for items
QUALITY_LEVELS = {
    0: 'Normal',
    1: 'Silver',
    2: 'Gold',
    4: 'Iridium'
}

# Comprehensive item database
# Format: id: {name, category, source, season, location, sell_price, acquisition_guide}
ITEM_DATABASE = {
    # CROPS - Spring
    '24': {
        'name': 'Parsnip',
        'category': 'crop',
        'source': 'farming',
        'season': 'spring',
        'location': 'farm',
        'sell_price': 35,
        'acquisition': 'Buy Parsnip Seeds from Pierre\'s General Store (20g), plant in spring, harvest in 4 days'
    },
    '188': {
        'name': 'Green Bean',
        'category': 'crop',
        'source': 'farming',
        'season': 'spring',
        'location': 'farm',
        'sell_price': 40,
        'acquisition': 'Buy Bean Starter from Pierre\'s (60g), plant in spring, harvest in 10 days (continues producing)'
    },
    '190': {
        'name': 'Cauliflower',
        'category': 'crop',
        'source': 'farming',
        'season': 'spring',
        'location': 'farm',
        'sell_price': 175,
        'acquisition': 'Buy Cauliflower Seeds from Pierre\'s (80g), plant in spring, harvest in 12 days'
    },
    '192': {
        'name': 'Potato',
        'category': 'crop',
        'source': 'farming',
        'season': 'spring',
        'location': 'farm',
        'sell_price': 80,
        'acquisition': 'Buy Potato Seeds from Pierre\'s (50g), plant in spring, harvest in 6 days'
    },

    # CROPS - Summer
    '254': {
        'name': 'Melon',
        'category': 'crop',
        'source': 'farming',
        'season': 'summer',
        'location': 'farm',
        'sell_price': 250,
        'acquisition': 'Buy Melon Seeds from Pierre\'s (80g), plant in summer, harvest in 12 days'
    },
    '256': {
        'name': 'Tomato',
        'category': 'crop',
        'source': 'farming',
        'season': 'summer',
        'location': 'farm',
        'sell_price': 60,
        'acquisition': 'Buy Tomato Seeds from Pierre\'s (50g), plant in summer, harvest in 11 days (continues producing)'
    },
    '258': {
        'name': 'Blueberry',
        'category': 'crop',
        'source': 'farming',
        'season': 'summer',
        'location': 'farm',
        'sell_price': 50,
        'acquisition': 'Buy Blueberry Seeds from Pierre\'s (80g), plant in summer, harvest in 13 days (continues producing)'
    },
    '260': {
        'name': 'Hot Pepper',
        'category': 'crop',
        'source': 'farming',
        'season': 'summer',
        'location': 'farm',
        'sell_price': 40,
        'acquisition': 'Buy Pepper Seeds from Pierre\'s (40g), plant in summer, harvest in 5 days (continues producing)'
    },
    '262': {
        'name': 'Wheat',
        'category': 'crop',
        'source': 'farming',
        'season': 'summer/fall',
        'location': 'farm',
        'sell_price': 25,
        'acquisition': 'Buy Wheat Seeds from Pierre\'s (10g), plant in summer or fall, harvest in 4 days'
    },
    '264': {
        'name': 'Radish',
        'category': 'crop',
        'source': 'farming',
        'season': 'summer',
        'location': 'farm',
        'sell_price': 90,
        'acquisition': 'Buy Radish Seeds from Pierre\'s (40g), plant in summer, harvest in 6 days'
    },

    # CROPS - Fall
    '270': {
        'name': 'Corn',
        'category': 'crop',
        'source': 'farming',
        'season': 'summer/fall',
        'location': 'farm',
        'sell_price': 50,
        'acquisition': 'Buy Corn Seeds from Pierre\'s (150g), plant in summer or fall, harvest in 14 days (continues producing)'
    },
    '272': {
        'name': 'Eggplant',
        'category': 'crop',
        'source': 'farming',
        'season': 'fall',
        'location': 'farm',
        'sell_price': 60,
        'acquisition': 'Buy Eggplant Seeds from Pierre\'s (20g), plant in fall, harvest in 5 days (continues producing)'
    },
    '274': {
        'name': 'Artichoke',
        'category': 'crop',
        'source': 'farming',
        'season': 'fall',
        'location': 'farm',
        'sell_price': 160,
        'acquisition': 'Buy Artichoke Seeds from Pierre\'s (30g), plant in fall, harvest in 8 days'
    },
    '276': {
        'name': 'Pumpkin',
        'category': 'crop',
        'source': 'farming',
        'season': 'fall',
        'location': 'farm',
        'sell_price': 320,
        'acquisition': 'Buy Pumpkin Seeds from Pierre\'s (100g), plant in fall, harvest in 13 days'
    },
    '278': {
        'name': 'Bok Choy',
        'category': 'crop',
        'source': 'farming',
        'season': 'fall',
        'location': 'farm',
        'sell_price': 80,
        'acquisition': 'Buy Bok Choy Seeds from Pierre\'s (50g), plant in fall, harvest in 4 days'
    },
    '280': {
        'name': 'Yam',
        'category': 'crop',
        'source': 'farming',
        'season': 'fall',
        'location': 'farm',
        'sell_price': 160,
        'acquisition': 'Buy Yam Seeds from Pierre\'s (60g), plant in fall, harvest in 10 days'
    },

    # FORAGING - Spring
    '16': {
        'name': 'Wild Horseradish',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'spring',
        'location': 'all areas',
        'sell_price': 50,
        'acquisition': 'Forage on the ground in spring (all areas)'
    },
    '18': {
        'name': 'Daffodil',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'spring',
        'location': 'all areas',
        'sell_price': 30,
        'acquisition': 'Forage on the ground in spring (all areas)'
    },
    '20': {
        'name': 'Leek',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'spring',
        'location': 'all areas',
        'sell_price': 60,
        'acquisition': 'Forage on the ground in spring (all areas)'
    },
    '22': {
        'name': 'Dandelion',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'spring',
        'location': 'all areas',
        'sell_price': 40,
        'acquisition': 'Forage on the ground in spring (all areas)'
    },

    # FORAGING - Summer
    '396': {
        'name': 'Spice Berry',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'summer',
        'location': 'all areas',
        'sell_price': 80,
        'acquisition': 'Forage on the ground in summer (all areas)'
    },
    '398': {
        'name': 'Grape',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'summer',
        'location': 'all areas',
        'sell_price': 80,
        'acquisition': 'Forage on the ground in summer (all areas)'
    },
    '402': {
        'name': 'Sweet Pea',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'summer',
        'location': 'all areas',
        'sell_price': 50,
        'acquisition': 'Forage on the ground in summer (all areas)'
    },

    # FORAGING - Fall
    '404': {
        'name': 'Common Mushroom',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'spring/fall',
        'location': 'all areas',
        'sell_price': 40,
        'acquisition': 'Forage in Secret Woods or mushroom cave, or in fall in all areas'
    },
    '406': {
        'name': 'Wild Plum',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'fall',
        'location': 'all areas',
        'sell_price': 80,
        'acquisition': 'Forage on the ground in fall (all areas)'
    },
    '408': {
        'name': 'Hazelnut',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'fall',
        'location': 'all areas',
        'sell_price': 90,
        'acquisition': 'Forage on the ground in fall (all areas)'
    },
    '410': {
        'name': 'Blackberry',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'fall',
        'location': 'all areas',
        'sell_price': 20,
        'acquisition': 'Forage on the ground in fall (all areas)'
    },

    # FORAGING - Winter
    '412': {
        'name': 'Winter Root',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'winter',
        'location': 'all areas',
        'sell_price': 70,
        'acquisition': 'Forage by tilling soil in winter (all areas)'
    },
    '414': {
        'name': 'Crystal Fruit',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'winter',
        'location': 'all areas',
        'sell_price': 150,
        'acquisition': 'Forage on the ground in winter (all areas)'
    },
    '416': {
        'name': 'Snow Yam',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'winter',
        'location': 'all areas',
        'sell_price': 100,
        'acquisition': 'Forage by tilling soil in winter (all areas)'
    },
    '418': {
        'name': 'Crocus',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'winter',
        'location': 'all areas',
        'sell_price': 60,
        'acquisition': 'Forage on the ground in winter (all areas)'
    },

    # FORAGING - Special
    '420': {
        'name': 'Red Mushroom',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'summer/fall',
        'location': 'Secret Woods, caves',
        'sell_price': 75,
        'acquisition': 'Forage in Secret Woods, mushroom cave, or Mines'
    },
    '422': {
        'name': 'Purple Mushroom',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'any',
        'location': 'caves',
        'sell_price': 250,
        'acquisition': 'Forage in the Mines or Skull Cavern'
    },
    '257': {
        'name': 'Morel',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'spring',
        'location': 'Secret Woods',
        'sell_price': 150,
        'acquisition': 'Forage in Secret Woods during spring'
    },
    '281': {
        'name': 'Chanterelle',
        'category': 'foraging',
        'source': 'foraging',
        'season': 'fall',
        'location': 'Secret Woods',
        'sell_price': 160,
        'acquisition': 'Forage in Secret Woods during fall'
    },

    # FRUITS
    '613': {
        'name': 'Apple',
        'category': 'fruit',
        'source': 'fruit_tree',
        'season': 'fall',
        'location': 'farm',
        'sell_price': 100,
        'acquisition': 'Plant an Apple Sapling (4,000g from Pierre\'s), wait 28 days, harvest in fall'
    },
    '634': {
        'name': 'Apricot',
        'category': 'fruit',
        'source': 'fruit_tree',
        'season': 'spring',
        'location': 'farm',
        'sell_price': 50,
        'acquisition': 'Plant an Apricot Sapling (2,000g from Pierre\'s), wait 28 days, harvest in spring'
    },
    '635': {
        'name': 'Orange',
        'category': 'fruit',
        'source': 'fruit_tree',
        'season': 'summer',
        'location': 'farm',
        'sell_price': 100,
        'acquisition': 'Plant an Orange Sapling (4,000g from Pierre\'s), wait 28 days, harvest in summer'
    },
    '636': {
        'name': 'Peach',
        'category': 'fruit',
        'source': 'fruit_tree',
        'season': 'summer',
        'location': 'farm',
        'sell_price': 140,
        'acquisition': 'Plant a Peach Sapling (6,000g from Pierre\'s), wait 28 days, harvest in summer'
    },
    '637': {
        'name': 'Pomegranate',
        'category': 'fruit',
        'source': 'fruit_tree',
        'season': 'fall',
        'location': 'farm',
        'sell_price': 140,
        'acquisition': 'Plant a Pomegranate Sapling (6,000g from Pierre\'s), wait 28 days, harvest in fall'
    },
    '638': {
        'name': 'Cherry',
        'category': 'fruit',
        'source': 'fruit_tree',
        'season': 'spring',
        'location': 'farm',
        'sell_price': 80,
        'acquisition': 'Plant a Cherry Sapling (3,400g from Pierre\'s), wait 28 days, harvest in spring'
    },

    # ANIMAL PRODUCTS
    '176': {
        'name': 'Egg',
        'category': 'animal_product',
        'source': 'chickens',
        'season': 'any',
        'location': 'coop',
        'sell_price': 50,
        'acquisition': 'Raise chickens in a coop, collect daily'
    },
    '180': {
        'name': 'Egg (Brown)',
        'category': 'animal_product',
        'source': 'chickens',
        'season': 'any',
        'location': 'coop',
        'sell_price': 50,
        'acquisition': 'Raise brown chickens in a coop, collect daily'
    },
    '182': {
        'name': 'Large Egg',
        'category': 'animal_product',
        'source': 'chickens',
        'season': 'any',
        'location': 'coop',
        'sell_price': 95,
        'acquisition': 'Raise high-friendship chickens in a coop, collect daily'
    },
    '184': {
        'name': 'Large Egg (Brown)',
        'category': 'animal_product',
        'source': 'chickens',
        'season': 'any',
        'location': 'coop',
        'sell_price': 95,
        'acquisition': 'Raise high-friendship brown chickens in a coop, collect daily'
    },
    '186': {
        'name': 'Large Milk',
        'category': 'animal_product',
        'source': 'cows',
        'season': 'any',
        'location': 'barn',
        'sell_price': 190,
        'acquisition': 'Raise high-friendship cows in a barn, milk daily'
    },
    '436': {
        'name': 'Goat Milk',
        'category': 'animal_product',
        'source': 'goats',
        'season': 'any',
        'location': 'barn',
        'sell_price': 225,
        'acquisition': 'Raise goats in a Big Barn, milk every 2 days'
    },
    '438': {
        'name': 'Large Goat Milk',
        'category': 'animal_product',
        'source': 'goats',
        'season': 'any',
        'location': 'barn',
        'sell_price': 345,
        'acquisition': 'Raise high-friendship goats in a Big Barn, milk every 2 days'
    },
    '440': {
        'name': 'Wool',
        'category': 'animal_product',
        'source': 'sheep/rabbits',
        'season': 'any',
        'location': 'barn/coop',
        'sell_price': 340,
        'acquisition': 'Raise sheep in a Deluxe Barn or rabbits in a Deluxe Coop, collect every 3 days'
    },
    '442': {
        'name': 'Duck Egg',
        'category': 'animal_product',
        'source': 'ducks',
        'season': 'any',
        'location': 'coop',
        'sell_price': 95,
        'acquisition': 'Raise ducks in a Big Coop, collect every 2 days'
    },
    '444': {
        'name': 'Duck Feather',
        'category': 'animal_product',
        'source': 'ducks',
        'season': 'any',
        'location': 'coop',
        'sell_price': 250,
        'acquisition': 'Raise ducks in a Big Coop, collect randomly (chance increases with friendship)'
    },
    '446': {
        'name': 'Rabbit\'s Foot',
        'category': 'animal_product',
        'source': 'rabbits',
        'season': 'any',
        'location': 'coop',
        'sell_price': 565,
        'acquisition': 'Raise rabbits in a Deluxe Coop, collect randomly (very rare, increases with friendship)'
    },
    '178': {
        'name': 'Hay',
        'category': 'animal_product',
        'source': 'farming',
        'season': 'any',
        'location': 'farm',
        'sell_price': 0,
        'acquisition': 'Cut grass with a scythe, or buy from Marnie (50g each)'
    },

    # ARTISAN GOODS
    '340': {
        'name': 'Honey',
        'category': 'artisan_goods',
        'source': 'bee_house',
        'season': 'spring/summer/fall',
        'location': 'farm',
        'sell_price': 100,
        'acquisition': 'Place a Bee House outside during spring, summer, or fall, collect every 4 days'
    },
    '424': {
        'name': 'Cheese',
        'category': 'artisan_goods',
        'source': 'cheese_press',
        'season': 'any',
        'location': 'farm',
        'sell_price': 230,
        'acquisition': 'Place Milk in a Cheese Press, wait 3 hours'
    },
    '426': {
        'name': 'Goat Cheese',
        'category': 'artisan_goods',
        'source': 'cheese_press',
        'season': 'any',
        'location': 'farm',
        'sell_price': 400,
        'acquisition': 'Place Goat Milk in a Cheese Press, wait 3 hours'
    },
    '428': {
        'name': 'Cloth',
        'category': 'artisan_goods',
        'source': 'loom',
        'season': 'any',
        'location': 'farm',
        'sell_price': 470,
        'acquisition': 'Place Wool in a Loom, wait 4 hours'
    },
    '432': {
        'name': 'Truffle Oil',
        'category': 'artisan_goods',
        'source': 'oil_maker',
        'season': 'any',
        'location': 'farm',
        'sell_price': 1065,
        'acquisition': 'Place a Truffle in an Oil Maker, wait 6 hours'
    },
    '306': {
        'name': 'Mayonnaise',
        'category': 'artisan_goods',
        'source': 'mayonnaise_machine',
        'season': 'any',
        'location': 'farm',
        'sell_price': 190,
        'acquisition': 'Place an Egg in a Mayonnaise Machine, wait 3 hours'
    },
    '307': {
        'name': 'Duck Mayonnaise',
        'category': 'artisan_goods',
        'source': 'mayonnaise_machine',
        'season': 'any',
        'location': 'farm',
        'sell_price': 375,
        'acquisition': 'Place a Duck Egg in a Mayonnaise Machine, wait 3 hours'
    },
    '348': {
        'name': 'Wine',
        'category': 'artisan_goods',
        'source': 'keg',
        'season': 'any',
        'location': 'farm',
        'sell_price': 300,
        'acquisition': 'Place any fruit in a Keg, wait 7 days'
    },
    '350': {
        'name': 'Juice',
        'category': 'artisan_goods',
        'source': 'keg',
        'season': 'any',
        'location': 'farm',
        'sell_price': 150,
        'acquisition': 'Place any vegetable in a Keg, wait 3 days'
    },
    '725': {
        'name': 'Oak Resin',
        'category': 'artisan_goods',
        'source': 'tapper',
        'season': 'any',
        'location': 'farm',
        'sell_price': 150,
        'acquisition': 'Place a Tapper on an Oak Tree, collect every 6-7 days'
    },
    '726': {
        'name': 'Pine Tar',
        'category': 'artisan_goods',
        'source': 'tapper',
        'season': 'any',
        'location': 'farm',
        'sell_price': 100,
        'acquisition': 'Place a Tapper on a Pine Tree, collect every 5-6 days'
    },
    '724': {
        'name': 'Maple Syrup',
        'category': 'artisan_goods',
        'source': 'tapper',
        'season': 'any',
        'location': 'farm',
        'sell_price': 200,
        'acquisition': 'Place a Tapper on a Maple Tree, collect every 9 days'
    },

    # FISH - Ocean
    '128': {
        'name': 'Pufferfish',
        'category': 'fish',
        'source': 'fishing',
        'season': 'summer',
        'location': 'ocean',
        'sell_price': 200,
        'acquisition': 'Fish in the ocean on sunny days during summer, 12pm-4pm'
    },
    '129': {
        'name': 'Anchovy',
        'category': 'fish',
        'source': 'fishing',
        'season': 'spring/fall',
        'location': 'ocean',
        'sell_price': 30,
        'acquisition': 'Fish in the ocean during spring or fall, any time'
    },
    '130': {
        'name': 'Tuna',
        'category': 'fish',
        'source': 'fishing',
        'season': 'summer/winter',
        'location': 'ocean',
        'sell_price': 100,
        'acquisition': 'Fish in the ocean during summer or winter, 6am-7pm'
    },
    '131': {
        'name': 'Sardine',
        'category': 'fish',
        'source': 'fishing',
        'season': 'spring/fall/winter',
        'location': 'ocean',
        'sell_price': 40,
        'acquisition': 'Fish in the ocean during spring, fall, or winter, 6am-7pm'
    },
    '132': {
        'name': 'Bream',
        'category': 'fish',
        'source': 'fishing',
        'season': 'any',
        'location': 'river',
        'sell_price': 45,
        'acquisition': 'Fish in the river during any season, 6pm-2am'
    },
    '136': {
        'name': 'Largemouth Bass',
        'category': 'fish',
        'source': 'fishing',
        'season': 'any',
        'location': 'mountain lake',
        'sell_price': 100,
        'acquisition': 'Fish in the mountain lake during any season, 6am-7pm'
    },
    '137': {
        'name': 'Smallmouth Bass',
        'category': 'fish',
        'source': 'fishing',
        'season': 'spring/fall',
        'location': 'river',
        'sell_price': 50,
        'acquisition': 'Fish in the river or forest pond during spring or fall, any time'
    },
    '138': {
        'name': 'Rainbow Trout',
        'category': 'fish',
        'source': 'fishing',
        'season': 'summer',
        'location': 'river',
        'sell_price': 65,
        'acquisition': 'Fish in the river or mountain lake during summer, 6am-7pm'
    },
    '139': {
        'name': 'Salmon',
        'category': 'fish',
        'source': 'fishing',
        'season': 'fall',
        'location': 'river',
        'sell_price': 75,
        'acquisition': 'Fish in the river during fall, 6am-7pm'
    },
    '140': {
        'name': 'Walleye',
        'category': 'fish',
        'source': 'fishing',
        'season': 'fall/winter',
        'location': 'river/pond',
        'sell_price': 105,
        'acquisition': 'Fish in rivers, ponds, or forest pond during fall or winter, rainy days, 12pm-2am'
    },
    '141': {
        'name': 'Perch',
        'category': 'fish',
        'source': 'fishing',
        'season': 'winter',
        'location': 'river',
        'sell_price': 55,
        'acquisition': 'Fish in the river, mountain lake, or forest pond during winter, any time'
    },
    '142': {
        'name': 'Carp',
        'category': 'fish',
        'source': 'fishing',
        'season': 'any',
        'location': 'mountain lake/Secret Woods',
        'sell_price': 30,
        'acquisition': 'Fish in mountain lake, Secret Woods pond, or sewers any season, any time'
    },
    '143': {
        'name': 'Catfish',
        'category': 'fish',
        'source': 'fishing',
        'season': 'spring/fall',
        'location': 'river/Secret Woods',
        'sell_price': 200,
        'acquisition': 'Fish in rivers or Secret Woods during spring or fall, rainy days, 6am-12am'
    },
    '144': {
        'name': 'Pike',
        'category': 'fish',
        'source': 'fishing',
        'season': 'summer/winter',
        'location': 'river',
        'sell_price': 100,
        'acquisition': 'Fish in the river, forest pond during summer or winter, any time'
    },
    '145': {
        'name': 'Sunfish',
        'category': 'fish',
        'source': 'fishing',
        'season': 'spring/summer',
        'location': 'river',
        'sell_price': 30,
        'acquisition': 'Fish in the river during spring or summer, sunny days, 6am-7pm'
    },
    '146': {
        'name': 'Red Mullet',
        'category': 'fish',
        'source': 'fishing',
        'season': 'summer/winter',
        'location': 'ocean',
        'sell_price': 75,
        'acquisition': 'Fish in the ocean during summer or winter, 6am-7pm'
    },
    '147': {
        'name': 'Herring',
        'category': 'fish',
        'source': 'fishing',
        'season': 'spring/winter',
        'location': 'ocean',
        'sell_price': 30,
        'acquisition': 'Fish in the ocean during spring or winter, any time'
    },
    '148': {
        'name': 'Eel',
        'category': 'fish',
        'source': 'fishing',
        'season': 'spring/fall',
        'location': 'ocean',
        'sell_price': 85,
        'acquisition': 'Fish in the ocean during spring or fall, rainy days, 4pm-2am'
    },
    '149': {
        'name': 'Octopus',
        'category': 'fish',
        'source': 'fishing',
        'season': 'summer',
        'location': 'ocean',
        'sell_price': 150,
        'acquisition': 'Fish in the ocean during summer, 6am-1pm'
    },
    '150': {
        'name': 'Red Snapper',
        'category': 'fish',
        'source': 'fishing',
        'season': 'summer/fall',
        'location': 'ocean',
        'sell_price': 50,
        'acquisition': 'Fish in the ocean during summer or fall, rainy days, 6am-7pm'
    },
    '151': {
        'name': 'Squid',
        'category': 'fish',
        'source': 'fishing',
        'season': 'winter',
        'location': 'ocean',
        'sell_price': 80,
        'acquisition': 'Fish in the ocean during winter, 6pm-2am'
    },
    '154': {
        'name': 'Sea Cucumber',
        'category': 'fish',
        'source': 'fishing',
        'season': 'fall/winter',
        'location': 'ocean',
        'sell_price': 75,
        'acquisition': 'Fish in the ocean during fall or winter, 6am-7pm'
    },
    '155': {
        'name': 'Super Cucumber',
        'category': 'fish',
        'source': 'fishing',
        'season': 'summer/fall',
        'location': 'ocean',
        'sell_price': 250,
        'acquisition': 'Fish in the ocean during summer or fall, 6pm-2am'
    },
    '156': {
        'name': 'Ghostfish',
        'category': 'fish',
        'source': 'fishing',
        'season': 'any',
        'location': 'mines',
        'sell_price': 45,
        'acquisition': 'Fish in the underground lake in the Mines (levels 20 and 60), any season'
    },
    '158': {
        'name': 'Stonefish',
        'category': 'fish',
        'source': 'fishing',
        'season': 'any',
        'location': 'mines',
        'sell_price': 300,
        'acquisition': 'Fish in the underground lake in the Mines (level 20), any season'
    },
    '159': {
        'name': 'Crimsonfish',
        'category': 'fish',
        'source': 'fishing',
        'season': 'summer',
        'location': 'ocean',
        'sell_price': 1500,
        'acquisition': 'Legendary fish - Fish at the east pier on the beach during summer, 6am-8pm (requires fishing level 5)'
    },
    '160': {
        'name': 'Angler',
        'category': 'fish',
        'source': 'fishing',
        'season': 'fall',
        'location': 'river',
        'sell_price': 900,
        'acquisition': 'Legendary fish - Fish north of Joja Mart during fall, any time (requires fishing level 3)'
    },
    '161': {
        'name': 'Ice Pip',
        'category': 'fish',
        'source': 'fishing',
        'season': 'any',
        'location': 'mines',
        'sell_price': 500,
        'acquisition': 'Fish in the underground lake in the Mines (level 60), any season'
    },
    '162': {
        'name': 'Lava Eel',
        'category': 'fish',
        'source': 'fishing',
        'season': 'any',
        'location': 'mines',
        'sell_price': 700,
        'acquisition': 'Fish in the lava lake in the Mines (level 100), any season'
    },
    '163': {
        'name': 'Legend',
        'category': 'fish',
        'source': 'fishing',
        'season': 'spring',
        'location': 'mountain lake',
        'sell_price': 5000,
        'acquisition': 'Legendary fish - Fish in the mountain lake during spring, rainy days, 6am-8pm (requires fishing level 10)'
    },
    '164': {
        'name': 'Sandfish',
        'category': 'fish',
        'source': 'fishing',
        'season': 'any',
        'location': 'desert',
        'sell_price': 75,
        'acquisition': 'Fish in the desert during any season, 6am-8pm'
    },
    '165': {
        'name': 'Scorpion Carp',
        'category': 'fish',
        'source': 'fishing',
        'season': 'any',
        'location': 'desert',
        'sell_price': 150,
        'acquisition': 'Fish in the desert during any season, 6am-8pm'
    },

    # MINERALS
    '334': {
        'name': 'Copper Bar',
        'category': 'metal_bar',
        'source': 'smelting',
        'season': 'any',
        'location': 'furnace',
        'sell_price': 60,
        'acquisition': 'Smelt 5 Copper Ore in a furnace with 1 coal'
    },
    '335': {
        'name': 'Iron Bar',
        'category': 'metal_bar',
        'source': 'smelting',
        'season': 'any',
        'location': 'furnace',
        'sell_price': 120,
        'acquisition': 'Smelt 5 Iron Ore in a furnace with 1 coal'
    },
    '336': {
        'name': 'Gold Bar',
        'category': 'metal_bar',
        'source': 'smelting',
        'season': 'any',
        'location': 'furnace',
        'sell_price': 250,
        'acquisition': 'Smelt 5 Gold Ore in a furnace with 1 coal'
    },
    '337': {
        'name': 'Iridium Bar',
        'category': 'metal_bar',
        'source': 'smelting',
        'season': 'any',
        'location': 'furnace',
        'sell_price': 1000,
        'acquisition': 'Smelt 5 Iridium Ore in a furnace with 1 coal (found in Skull Cavern)'
    },
    '338': {
        'name': 'Refined Quartz',
        'category': 'refined',
        'source': 'smelting',
        'season': 'any',
        'location': 'furnace',
        'sell_price': 50,
        'acquisition': 'Smelt 1 Quartz in a furnace with 1 coal, or recycle broken glasses/CDs'
    },
    '80': {
        'name': 'Quartz',
        'category': 'mineral',
        'source': 'mining',
        'season': 'any',
        'location': 'mines',
        'sell_price': 25,
        'acquisition': 'Mine rocks in the Mines or Skull Cavern'
    },
    '82': {
        'name': 'Fire Quartz',
        'category': 'mineral',
        'source': 'mining',
        'season': 'any',
        'location': 'mines',
        'sell_price': 100,
        'acquisition': 'Mine in the Mines levels 80+ or pan in rivers'
    },
    '84': {
        'name': 'Frozen Tear',
        'category': 'mineral',
        'source': 'mining',
        'season': 'any',
        'location': 'mines',
        'sell_price': 75,
        'acquisition': 'Mine in the Mines levels 40-79 or crack open geodes'
    },
    '86': {
        'name': 'Earth Crystal',
        'category': 'mineral',
        'source': 'mining',
        'season': 'any',
        'location': 'mines',
        'sell_price': 50,
        'acquisition': 'Mine in the Mines levels 1-39 or crack open geodes'
    },

    # SPECIAL
    'gold': {
        'name': 'Gold',
        'category': 'currency',
        'source': 'various',
        'season': 'any',
        'location': 'various',
        'sell_price': 1,
        'acquisition': 'Earn gold by selling items, completing quests, mining, or fishing'
    },
}


def get_item_info(item_id):
    """
    Get item information by ID.

    Args:
        item_id: String or int item ID

    Returns:
        dict: Item information including name, category, source, acquisition guide
    """
    item_id_str = str(item_id)
    return ITEM_DATABASE.get(item_id_str, {
        'name': f'Unknown Item ({item_id})',
        'category': 'unknown',
        'source': 'unknown',
        'season': 'unknown',
        'location': 'unknown',
        'sell_price': 0,
        'acquisition': 'Check the Stardew Valley Wiki for more information'
    })


def get_item_name(item_id):
    """
    Get item name by ID.

    Args:
        item_id: String or int item ID

    Returns:
        str: Item name
    """
    return get_item_info(item_id)['name']


def get_item_acquisition_guide(item_id):
    """
    Get acquisition guide for an item.

    Args:
        item_id: String or int item ID

    Returns:
        str: How to obtain the item
    """
    return get_item_info(item_id)['acquisition']


def get_quality_name(quality_level):
    """
    Get quality name by level.

    Args:
        quality_level: int (0=Normal, 1=Silver, 2=Gold, 4=Iridium)

    Returns:
        str: Quality name
    """
    return QUALITY_LEVELS.get(quality_level, 'Normal')


def get_wiki_url(item_id):
    """
    Generate Stardew Valley Wiki URL for an item.

    Args:
        item_id: String or int item ID

    Returns:
        str: Wiki URL for the item
    """
    item_name = get_item_name(item_id)
    if item_name.startswith('Unknown Item'):
        return 'https://stardewvalleywiki.com/'

    # Replace spaces with underscores for wiki URL
    wiki_name = item_name.replace(' ', '_').replace("'", "%27")
    return f'https://stardewvalleywiki.com/{wiki_name}'


def get_items_by_category(category):
    """
    Get all items in a specific category.

    Args:
        category: str (e.g., 'crop', 'fish', 'foraging', 'animal_product')

    Returns:
        dict: Items in the category {id: item_info}
    """
    return {
        item_id: item_info
        for item_id, item_info in ITEM_DATABASE.items()
        if item_info['category'] == category
    }


def get_items_by_season(season):
    """
    Get all items available in a specific season.

    Args:
        season: str ('spring', 'summer', 'fall', 'winter', 'any')

    Returns:
        dict: Items available in the season {id: item_info}
    """
    return {
        item_id: item_info
        for item_id, item_info in ITEM_DATABASE.items()
        if season.lower() in item_info['season'].lower() or item_info['season'] == 'any'
    }


# Example usage
if __name__ == '__main__':
    # Test item lookup
    print(get_item_name('725'))  # Oak Resin
    print(get_item_acquisition_guide('637'))  # Pomegranate
    print(get_wiki_url('613'))  # Apple

    # Test category lookup
    spring_crops = get_items_by_category('crop')
    print(f"\nFound {len(spring_crops)} crops in database")

    # Test season lookup
    spring_items = get_items_by_season('spring')
    print(f"Found {len(spring_items)} spring items in database")
