const setupMapKitJs = async() => {
    if (!window.mapkit || window.mapkit.loadedLibraries.length === 0) {
        await new Promise(resolve => { window.initMapKit = resolve });
        delete window.initMapKit;
    }
    // const jwt = fetch_jwt()
    const jwt = ""
    mapkit.init({
        authorizationCallback: done => { done(jwt); }
    });
};

const main = async () => {
    await setupMapKitJs();
    const cambridge = new mapkit.CoordinateRegion(
        new mapkit.Coordinate(21.3184119, -157.8647806),
        new mapkit.CoordinateSpan(0.107647972, 0.124985255)
    );
    const map = new mapkit.Map("map-container");
    
    map.region = cambridge;
};

main()
