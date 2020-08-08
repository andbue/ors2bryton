from sys import argv
from os.path import splitext
from lxml import etree
from struct import pack


def main():
    print(argv)
    gpx = argv[1]

    """
    bryton:
         1: go ahead
         2: right
         3: left
         4: slight right
         5: slight left
         6: close right
         7: close left
         8: exit right
         9: exit left
        10: continue straight
        11: uturn right
        12: uturn left
        13++: go ahead

    openrouteservice:
    (https://github.com/GIScience/openrouteservice/blob/master/openrouteservice/src/main/java/org/heigit/ors/routing/instructions/InstructionType.java)
        TURN_LEFT,              /*0*/
        TURN_RIGHT,             /*1*/
        TURN_SHARP_LEFT,        /*2*/
        TURN_SHARP_RIGHT,       /*3*/
        TURN_SLIGHT_LEFT,       /*4*/
        TURN_SLIGHT_RIGHT,      /*5*/
        CONTINUE,               /*6*/
        ENTER_ROUNDABOUT,       /*7*/
        EXIT_ROUNDABOUT,        /*8*/
        UTURN,                  /*9*/
        FINISH,                 /*10*/
        DEPART,                 /*11*/
        KEEP_LEFT,              /*12*/
        KEEP_RIGHT,             /*13*/
        UNKNOWN                 /*14*/;
    """
    orst2brt = {

        0: 3, 
        1: 2,
        2: 7,
        3: 6,
        4: 5,
        5: 4,
        6: 1,
        7: 10,
        8: 8,
        9: 12,
        10: 1,
        11: 1,
        12: 9,
        13: 8,
        14: 1
    }

    fname = splitext(gpx)[0]
    r = etree.parse(gpx).getroot()
    ns = r.nsmap[None]
    rte = r.find(f'./{{{ns}}}rte')
    rtepts = rte.findall(f'./{{{ns}}}rtept')
    unit = r.find(f'./{{{ns}}}extensions/{{{ns}}}distance-units').text
    uf = 10e2 if unit == "km" else 1
    ext = rte.find(f'./{{{ns}}}extensions') 

    dist = int(float(ext.find(f'./{{{ns}}}distance').text) * uf)
    bnds = ext.find(f'./{{{ns}}}bounds')
    bnds = {k: int(float(v) * 10e5) for k, v in bnds.attrib.items()}
    bnds = (bnds['maxLat'], bnds['minLat'], bnds['maxLon'], bnds['minLon'])
    
    print(f'{fname}.smy: {len(rtepts)} waypoints, distance {dist} meters.')
    with open(fname + '.smy', 'wb') as smy:
        smy.write(pack('<HHIIIII36x', 1, len(rtepts), *bnds, dist))

    with open(fname + '.tinfo', 'wb') as tinfo,\
         open(fname + '.track', 'wb') as track:
        step = None
        for n, p in enumerate(rtepts):
            lat = int(float(p.attrib.get('lat')) * 10e5)
            lon = int(float(p.attrib.get('lon')) * 10e5)
            track.write(pack('<II8x', lat, lon))
            
            thisstep = int(p.find(f'./{{{ns}}}extensions/{{{ns}}}step').text)
            if thisstep != step:
                name = p.find(f'./{{{ns}}}name').text
                name = name.encode() if name != None else "".encode()
                dist = int(float(p.find(f'./{{{ns}}}extensions/{{{ns}}}distance').text) * uf)
                dur = int(float(p.find(f'./{{{ns}}}extensions/{{{ns}}}duration').text))
                t = int(p.find(f'./{{{ns}}}extensions/{{{ns}}}type').text)
                d = orst2brt[t]
                tinfo.write(pack('<HBxHxxHxx32s', n, d, dist, dur, name))
                step = thisstep
    print(f'{fname}.tinfo, {fname}.track: Finished writing.')
            
if __name__ == "__main__":
    main()

