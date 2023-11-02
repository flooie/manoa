
function get_key() {
    const jwt = "{{token}}";
    return jwt
}
const setupMapKitJs = async() => {

    if (!window.mapkit || window.mapkit.loadedLibraries.length === 0) {
        // mapkit.core.js or the libraries are not loaded yet.
        // Set up the callback and wait for it to be called.
        await new Promise(resolve => { window.initMapKit = resolve });

        // Clean up
        delete window.initMapKit;
    }

    const jwt = get_key()

    mapkit.init({
        authorizationCallback: done => { done(jwt); }
    });
};

const main = async() => {
    await setupMapKitJs();

    // Landmarks data
    const sanFranciscoLandmarks = [
        {
            coordinate: new mapkit.Coordinate(21.306718, -157.865599),
            title: "1 Aloha Tower Dr",
            statute: "HRS XYZ",
            url: ""
        }
    ];


    // Offset between the callout and the associated annotation marker
    const offset = new DOMPoint(-148, -78);

    // Maps each annotation (key) to the landmark data describing it (value)
    const annotationsToLandmark = new Map();

    // Each annotation will use these functions to present a custom callout
    const landmarkAnnotationCallout = {

        calloutElementForAnnotation: annotation => {
            const landmark = annotationsToLandmark.get(annotation);

            const div = document.createElement("div");
            div.className = "landmark";

            const title = div.appendChild(document.createElement("h1"));
            title.textContent = landmark.title;

            const section = div.appendChild(document.createElement("section"));

            const statute = section.appendChild(document.createElement("p"));
            statute.className = "statute";
            statute.textContent = landmark.statute;

            const link = section.appendChild(document.createElement("p"));
            link.className = "homepage";

            const a = link.appendChild(document.createElement("a"));
            a.href = landmark.url;
            a.textContent = "website";

            return div;
        },

        calloutAnchorOffsetForAnnotation: (annotation, element) => offset,

        calloutAppearanceAnimationForAnnotation: annotation =>
            ".4s cubic-bezier(0.4, 0, 0, 1.5) " +
            "0s 1 normal scale-and-fadein"
    };

    for (const landmark of sanFranciscoLandmarks) {
        const annotation = new mapkit.MarkerAnnotation(landmark.coordinate, {
            callout: landmarkAnnotationCallout,
            color: "#c969e0"
        });

        annotationsToLandmark.set(annotation, landmark);
    }

    const map = new mapkit.Map("map");
    map.showItems(Array.from(annotationsToLandmark.keys()));
};

main();

