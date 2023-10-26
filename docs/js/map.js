
   function generate_new_map(coordinate_array) {
       $("#map").empty()
       const map = new mapkit.Map("map");
       const oahu = new mapkit.CoordinateRegion(

        new mapkit.Coordinate(21.2881919, -157.8279737),
        new mapkit.CoordinateSpan(0.167647972, 0.354985255)
    );

        // Create a map in the element whose ID is "map-container"
        map.region = oahu;
        const offset = new DOMPoint(-148, -78);

        const landmarkAnnotationCallout = {

            calloutElementForAnnotation: annotation => {
                const landmark = annotationsToLandmark.get(annotation);

                const div = document.createElement("div");
                div.className = "landmark";

                const title = div.appendChild(document.createElement("p"));
                title.textContent = landmark.title;

                const section = div.appendChild(document.createElement("section"));

                const statute = section.appendChild(document.createElement("p"));
                statute.className = "statute";
                statute.textContent = "landmark.statute";

                const link = section.appendChild(document.createElement("p"));
                link.className = "homepage";

                const a = link.appendChild(document.createElement("a"));
                a.href = "landmark.url";
                a.textContent = "website";

                return div;
            },

            calloutAnchorOffsetForAnnotation: (annotation, element) => offset,

            calloutAppearanceAnimationForAnnotation: annotation =>
                ".4s cubic-bezier(0.4, 0, 0, 1.5) " +
                "0s 1 normal scale-and-fadein"
        };


        const annotationsToLandmark = new Map();

       const data = JSON.parse(coordinate_array)
        for (let i = 0; i < data.length; i++) {

           var landmark = {
                coordinate: new mapkit.Coordinate(parseFloat(data[i][2]), parseFloat(data[i][1])),
                title: data[i][0],
                statute: "Location:",
                url: "url"
            };
           console.log("hello world")
        const annotation = new mapkit.MarkerAnnotation(landmark.coordinate, {
            callout: landmarkAnnotationCallout,
            color: "#c969e0"
        });
        annotationsToLandmark.set(annotation, landmark);
        }
       map.showItems(Array.from(annotationsToLandmark.keys()));
   }

