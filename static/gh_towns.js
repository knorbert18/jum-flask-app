document.addEventListener('DOMContentLoaded', function () {
  const regionsData = {
    "Greater Accra": {
      "Accra Metropolitan": ["Osu", "Adabraka", "Dansoman", "Teshie", "Nima", "La", "Mamprobi", "Ridge", "Labone", "Cantoments", "Dzorwulu", "Airport Residential", "Kwame Nkrumah Circle", "Darkuman", "Chorkor"],
      "Tema Metropolitan": ["Tema Community 1", "Community 2", "Community 4", "Community 5", "Community 11", "Community 25", "Kpone", "Ashaiman", "Prampram", "Nungua", "Sakumono", "Baatsona", "Spintex", "Sebrepor", "Kpone Bawaleshie"],
      "Ga South Municipal": ["Weija", "Mallam", "Gbawe", "Ngleshie Amanfro", "New Bortianor", "Domeabra", "Tuba", "Tetegu", "Oblogo", "McCarthy Hill", "Kokrobite", "Aplaku", "Fetteh Kakraba", "Kasoa", "Odorkor"],
      "Ga East Municipal": ["Abokobi", "Haatso", "Kwabenya", "Agbogba", "Ashongman", "Dome", "Atomic", "Pantang", "Kisseman", "Achimota", "North Legon", "Bohye", "Westlands", "Kwabenya Hills", "Dome Pillar 2"],
      "La Nkwantanang Madina": ["Madina", "Adenta", "Oyarifa", "Lashibi", "Ayi Mensah", "Pantang", "Teiman", "Ogbojo", "Redco", "Sakora", "Kekele", "Lartebiokorshie", "Koforidua Hills", "Ashiyie", "Ashaley Botwe", "Amanfrom New-Town"]
    },
    "Ashanti": {
      "Kumasi Metropolitan": ["Adum", "Asafo", "Amakom", "Bantama", "Suame", "Tafo", "Asokwa", "Oforikrom", "Atonsu", "Ayigya", "Kwadaso", "Ahinsan", "Patasi", "Buokrom", "Manhyia"],
      "Obuasi Municipal": ["Obuasi", "Tutuka", "Boete", "Bogobiri", "Brahabebome", "Anyinam", "Pomposo", "New Nsuta", "Sanso", "Bediem", "Kwabrafoso", "Ahansonyewodea", "Anwiankwanta", "Domeabra", "Mampamhwe"],
      "Ejisu Municipal": ["Ejisu", "Krapa", "Besease", "Onwe", "Kwaso", "Tikrom", "Fumesua", "Kokobra", "Bonwire", "Achinakrom", "Edwenase", "Abankro", "Odaho", "Apromase", "Ekyem"],
      "Mampong Municipal": ["Mampong", "Kofiase", "Asante Mampong", "Bosomkyekye", "Deduako", "Amoako", "Kofiase", "Effiduase", "Jamasi", "Bonkrong", "Adidwan", "Kyekyewere", "Adukrom", "Atonsu", "Sekyere"],
      "Bekwai Municipal": ["Bekwai", "Asante Bekwai", "Poano", "Feyiase", "Aboaso", "Konkoma", "Krofrom", "Senfi", "Anwiankwanta", "Kwapia", "Bodwesango", "Agyamankrom", "Subriso", "Dominase", "Asakyiri"]
    },
    "Western": {
      "Sekondi-Takoradi Metropolitan": ["Sekondi", "Takoradi", "Kwesimintsim", "Effiakuma", "Essikado", "Adientem", "Fijai", "Airport Ridge", "Ketan", "Whindo", "Tanokrom", "Apremdo", "Mpintsin", "New Takoradi", "Inchaban"],
      "Tarkwa Nsuaem Municipal": ["Tarkwa", "Nsuaem", "Aboso", "Tamso", "Brahabebome", "Bogoso", "Prestea", "Huni Valley", "Bompieso", "Wassa Akropong", "Damang", "Simpa", "Agona", "Awunakrom", "Dompim"],
      "Ahanta West Municipal": ["Agona Nkwanta", "Apowa", "Abura", "Ewusiejoe", "Busua", "Dixcove", "Aboadze", "Aboasi", "Kwesimintsim", "Akatakyiman", "Beyin", "Cape Three Points", "Ankobra", "Ampatano", "Otto-Kofi"],
      "Nzema East Municipal": ["Axim", "Ampain", "Eikwe", "Bakanta", "Anyanui", "Bonyere", "Akropong", "Esiama", "Baku", "Aiyinasi", "Gwira Aiyinase", "Gwira Wiawso", "Gwira Banso", "Ellembelle", "Salman"],
      "Ellembelle District": ["Nkroful", "Ankobra", "Kojokrom", "Esiama", "Asasetre", "Ajomoro", "Adubrim", "Kamgbunli", "Bamiankor", "Akropong", "Alabokazo", "Ayawaso", "Amankrom", "Asanda", "Awiebo"]
    },
    "Eastern": {
      "New Juaben South Municipal": ["Koforidua", "Oyoko", "Jumapo", "Srodae", "Adweso", "Effiduase", "Asokore", "Okorase", "Galloway", "Betom", "Zongo", "Mile 50", "Nsukwao", "Abogri", "Nkurakan"],
      "Akuapem North Municipal": ["Akropong", "Mampong", "Tutu", "Aburi", "Larteh", "Obosomase", "Ahwerase", "Mamfe", "Okorase", "Abonse", "Anum", "Adawso", "Bososo", "Aseseeso", "Amanokrom"],
      "Suhum Municipal": ["Suhum", "Asuboi", "Amanase", "Obretema", "Nankese", "Anum Apapam", "Apedwa", "Okorase", "Kraboa Coaltar", "Adakwa", "Tinkong", "Teacher Mante", "Omenako", "Akorabo", "Apirede"],
      "Nsawam Adoagyiri Municipal": ["Nsawam", "Adoagyiri", "Fotobi", "Panpanso", "Akwamu", "Ahwerease", "Owuraku", "Dobro", "Amamoley", "Adeiso", "Kyekyewere", "Kotoku", "Pakro", "Pepease", "Kwamekyere"],
      "West Akim Municipal": ["Asamankese", "Adeiso", "Osenase", "Abamkrom", "Amamprobi", "Aworasa", "Anamase", "Nyanoa", "Akim Awisa", "Kwabeng", "Oda", "Kotokuom", "Kwaobaa", "Esubone", "Otumi"],
      "Asuogyaman District": ["Akrade", "Atimpoku", "Akosombo", "Mpakadan", "Mangoase", "Boso", "Odupong", "Sakora", "Ehiamankyene", "Amanfrom", "Wemankor", "Kramokrom", "Ebuom", "Nyangua"],
      "Yilo Krobo District": ["Somanya", "Yilo", "Asesewa", "Klo-Begoro", "Nkurakan", "Dawhenya", "Kpong", "Obosomase", "Gbadago", "Kpone", "Okwenya", "Anfoega", "Ayikai", "Kokonya", "Ningo", "Ziope"],
      "Lower Manya Krobo District": ["Odumase", "Asite", "Dawhenya", "Yilo", "Kpong", "Larteh", "Aburi", "Mampong", "Akwamu", "Amanfro", "Nanya", "Ziope", "Aboabo", "Awe", "Kwakuo", "Torgome", "Ahinfie", "Sakora"],
    },

    "Central": {
      "Cape Coast Metropolitan": ["Cape Coast", "Kakumdo", "Pedu", "Abura", "Adisadel", "Apewosika", "Amamoma", "Ola", "Siwdo", "Efutu", "Kotokuraba", "Bakaano", "Aboom", "Kwaprow", "Abakam", "Mpeasem"],
      "Mfantsiman Municipal": ["Saltpond", "Anomabo", "Mankessim", "Biriwa", "Ankaful", "Abandze", "Kormantse", "Yamoransa", "Otuam", "Edumafa", "Narkwa", "Kyeakor", "Odoben", "Abura Dunkwa", "Kuntu"],
      "Awutu Senya East Municipal": ["Kasoa", "Oduponkpehe", "Ofankor", "Millennium City", "Opeikuma", "Obom Road", "Iron City", "Adam Nana", "Tuba Junction", "Nyanyano", "Akweley", "Ngleshie Amanfro", "Fetteh Kakraba", "Gomoa Nyanyano", "CP"],
      "Gomoa West District": ["Apam", "Gomoa Dawurampong", "Gomoa Achiase", "Gomoa Mampong", "Gomoa Aboso", "Gomoa Lome", "Gomoa Okyereko", "Gomoa Eshiem", "Gomoa Odumase", "Gomoa Brofo", "Gomoa Akropong", "Gomoa Jukwa", "Gomoa Nkum", "Gomoa Kyiren", "Gomoa Bisease"],
      "Assin North Municipal": ["Assin Fosu", "Domeabra", "Nyankumasi", "Assin Kushea", "Assin Praso", "Assin Nyankomase", "Assin Awisem", "Assin Manso", "Assin Akonfudi", "Assin Dansame", "Assin Jakai", "Assin Kruwa", "Assin Bediadua", "Assin Odumase", "Assin Atwereboanda"]
    },

    "Volta": {
      "Ho Municipal": ["Ho", "Anlokordzi", "Bankoe", "Heve", "Ahoe", "Kpeve", "Matse", "Taviefe", "Dzolo", "Klefe", "Akrofu", "Shia", "Kpedze", "Abutia", "Tanyigbe", "Hliha"],
      "Keta Municipal": ["Keta", "Anloga", "Abor", "Anlo Afiadenyigba", "Dzelukope", "Vodza", "Kedzi", "Havedzi", "Atorkor", "Anyako", "Woe", "Whuti", "Tegbi", "Srogboe", "Fiaxor"],
      "Hohoe Municipal": ["Hohoe", "Likpe", "Gbledi", "Gbi Wegbe", "Gbi Godenu", "Alavanyo", "Fodome", "Gbi Kpeme", "Lolobi", "Akpafu", "Santrokofi", "Bame", "Kledzo", "Have", "Kpeve"],
      "South Tongu District": ["Sogakope", "Adidome", "Tefle", "Vume", "Agortime", "Aboboyaa", "Sokpoe", "Tornu", "Dabala", "Dorfey", "Dabala Junction", "Togorme", "Agave", "Tunu", "Anyakpor"],
      "North Tongu District": ["Battor", "Mepe", "Aveyime", "Torgorme", "Podoe", "Kasseh", "Dorfor", "Vume", "Tagadzi", "Adidokpoe", "Agotime-Kpetoe", "Volivo", "Bakpa", "Fodzoku", "Battor Dugame"]
    },

    "Northern": {
      "Tamale Metropolitan": ["Tamale", "Lamashegu", "Choggu", "Kalpohin", "Zogbeli", "Sabonjida", "Sagnarigu", "Gumani", "Fuo", "Savelugu", "Kalariga", "Dohini", "Kanvili", "Vittin", "Bilpela"],
      "Sagnarigu Municipal": ["Sagnarigu", "Kanvili", "Jisonayili", "Kamina Barracks", "Vittin Estates", "Gurugu", "Katani", "Kukuo", "Choggu Yapalsi", "Mile 9", "Sognaayili", "Zagyuri", "Fuo", "Dungu", "Nobewam"],
      "Savelugu Municipal": ["Savelugu", "Diare", "Nanton", "Kpachelo", "Tolon", "Kumbungu", "Gurugu", "Lanaayili", "Kasuliyili", "Gbulahagu", "Zoggu", "Yipieliyili", "Pong Tamale", "Kukuobilla", "Libga"],
      "Karaga District": ["Karaga", "Pishigu", "Kumbungu", "Nyong Nayili", "Sakpe", "Kpatinga", "Jagrido", "Gundaa", "Zanteli", "Kasuliyili", "Bagurugu", "Liman Kare", "Kpachi", "Gunayili", "Dingoni"],
      "Gushegu Municipal": ["Gushegu", "Gbungbaliga", "Yapalsi", "Kpatinga", "Kpabia", "Zantili", "Gundaa", "Galwei", "Sakogu", "Kpabia", "Bogu", "Tali", "Nalerigu", "Damanko", "Nakpanduri"]
    },

    "Eastern": {
    "Koforidua Municipal": ["Koforidua", "Nsukwao", "New Juaben", "Boadi", "Effiduase", "Akwadum", "Asokore", "Birim South", "Aburi", "Larteh", "Osiem", "Fanteakwa", "Ayirebi", "Brewireso", "Akyem"]
  },
  "Volta": {
    "Ho Municipal": ["Ho", "Hohoe", "Tsito", "Abutia", "Peki", "Akatsi", "Aflao", "Wli", "Dzolokpuita", "Kpando", "Domeabra", "Tefle", "Aflawode", "Volo", "Adidome"]
  },
  
  "Savannah": {
    "Bole District": ["Bole", "Sawla", "Jinijini", "Junction", "Bambila", "Tunyinsa", "Narte", "Gbung", "Fidaa", "Fosu", "Wura", "Damongo", "Sung", "Sankore", "Jande"]
  },
  "Bono": {
    "Sunyani Municipal": ["Sunyani", "Wamfie", "Chiraa", "Berekum", "Nsoatre", "Abesim", "Kukuom", "Odumase", "Yenwom", "Seikwa", "Dadieso", "Badu", "Mim", "Moglaa", "Nkoranza"]
  },
  "Bono East": {
    "Techiman Municipal": ["Techiman", "Sampa", "Bamboi", "Buoyem", "Kintampo", "Donkro", "Pru West", "Baako", "Anum", "Kojokrom", "Busunya", "Tain", "Abofour", "Wamfie", "Tano North"]
  },
  "Ahafo": {
    "Goaso Municipal": ["Goaso", "Asunafo", "Bechem", "Kukuom", "Ntotroso", "Kukuom", "Ankwanta", "Nsuatre", "Dabonso", "Aboabo", "Abosso", "Kuma", "Sene", "Kokrokoo", "Fawoman"]
  },
  "Oti": {
    "Dambai Municipal": ["Dambai", "Kpassa", "Babile", "Asikuma", "Tatale", "Banda", "Bechem", "Abena", "Kpalime", "Nkwanta", "Asume", "Ebi", "Bongo", "Gongomba", "Bongoman"]
  },
  "Western North": {
    "Sefwi Wiawso Municipal": ["Sefwi Wiawso", "Sefwi Bekwai", "Sefwi Dwenase", "Sefwi Afere", "Sefwi Akontombra", "Sefwi Twidan", "Sefwi Amankwanta", "Sefwi Baako", "Sefwi Ntumkrom", "Sefwi Ntotroso", "Sefwi Atwedie", "Sefwi Anhwiaso", "Sefwi Abodwe", "Sefwi Bodwe", "Sefwi Kumfi"]
  }
};

  const regionSelect = document.getElementById('regionSelect');
  const districtSelect = document.getElementById('districtSelect');
  const townSelect = document.getElementById('townSelect');

  // Populate region dropdown
  for (let region in regionsData) {
    let option = new Option(region, region);
    regionSelect.add(option);
  }

  regionSelect.addEventListener('change', function () {
    let selectedRegion = regionSelect.value;

    // Clear previous selections
    districtSelect.innerHTML = "<option value=''>Select District</option>";
    townSelect.innerHTML = "<option value=''>Select Town</option>";

    if (selectedRegion) {
      let districts = regionsData[selectedRegion];
      for (let district in districts) {
        let option = new Option(district, district);
        districtSelect.add(option);
      }
    }
  });

  districtSelect.addEventListener('change', function () {
    let selectedRegion = regionSelect.value;
    let selectedDistrict = districtSelect.value;
    townSelect.innerHTML = "<option value=''>Select Town</option>";

    if (selectedRegion && selectedDistrict) {
      let towns = regionsData[selectedRegion][selectedDistrict];
      towns.forEach(town => {
        let option = new Option(town, town);
        townSelect.add(option);
      });
    }
  });
});
