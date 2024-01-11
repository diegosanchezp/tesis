import {startAlpine} from 'js/utils/alpine';
import cytoscape from 'cytoscape';
import elk from 'cytoscape-elk';
import tippy from 'tippy.js';
import 'tippy.js/dist/tippy.css';

import popper from 'cytoscape-popper';

cytoscape.use(popper);

const graphStoreObj = () => ({
    node_path: [],
    set_path(path: string[]){
        this.node_path = path
    }
})

startAlpine({
    stores: [
        {
            name: "graph",
            store: graphStoreObj,
            persist: false,
        }
    ],
    components: []
})

// Setup elk layout
cytoscape.use( elk );

const cy = cytoscape({
    // container to render in
    container: document.getElementById('cy'),
    // For 'single' the previous elements are unselected
    selectionType: 'single',
    // https://github.com/cytoscape/cytoscape.js-elk
    layout: {
        name: 'elk',
        elk: {

            algorithm: 'disco',
            componentLayoutAlgorithm: 'stress',
            // algorithm: 'stress',
            'elk.stress.desiredEdgeLength': 100,
            'elk.stress.epsilon': 0.000009,
        },
        fit: true,
        animate: false
    },
    style: [ // the stylesheet for the graph
        {
            selector: 'node',
            style: {
                'border-color': 'black',
                'border-width': 1,
                'border-style': 'solid',
                'background-color': 'white',
                'label': 'data(name)',
                'shape': 'round-rectangle',
                'width': '120px',
                "font-size": 10,
                "text-max-width": "100px",
                'height': '30',
                "text-wrap": "wrap",
                // This puts the text inside the node
                'text-valign': 'center',
                'text-halign': 'center',
            }
        },
        {
            selector: 'edge',
            style: {
                'width': 2,
                'line-color': '#ccc',
                'target-arrow-color': '#ccc',
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier'
            }
        }
    ],
    elements: [ // list of graph elements to start with
        {
            data: {
                id: 'ciencias',
                name: 'Ciencias',
                description: "",
            },
        },
        {
            data: {
                id: 'computacion',
                name: 'Computación',
                description: "",
            }
        },
        {
            data: {
                id: 'redes',
                name: 'Redes',
                description: "",
            }
        },
        {
            data: {
                id: 'arquitecto-redes',
                name: 'Arquitecto de redes',
                description: "",
            }
        },
        {
            data: {
                id: 'aplicaciones-con-tecnologias-internet' ,
                name: 'Aplicaciones con Tecnologías Internet',
                description: "Web stuff...",
            }
        },
        {
            data: {
                id: 'desarrollador-backend',
                name: 'Desarrollador backend',
                description: "Does everything",
            }
        },
        {
            data: {
                id: 'desarrollador-frontend',
                name: 'Desarrollador frontend',
                description: "Does only the web GUI",
            }
        },
        {
            data: {
                id: 'inteligencia-artificial',
                name: 'Inteligencia artificial',
                description: "Computer science black magic",
            }
        },
        {
            data: {
                id: 'analista-de-datos',
                name: 'Analista de datos',
                description: "Querys...",
            }
        },
        {
            data: {
                id: 'ai-data-trainer',
                name: 'Ai data trainer',
                description: "Trains the AI",
            }
        },
        // edge ab
        {
            data: { id: 'ciencias-computacion', source: 'ciencias', target: 'computacion' }
        },
        {
            data: { id: 'computacion-redes', source: 'computacion', target: 'redes' }
        },
        {
            data: { id: 'redes-arquitecto', source: 'redes', target: 'arquitecto-redes' }
        },
        {
            data: { id: 'computacion-aplicaciones-inter', source: 'computacion', target: 'aplicaciones-con-tecnologias-internet' }
        },

        {
            data: { id: 'computacion-inteligencia', source: 'computacion', target: 'inteligencia-artificial' }
        },
        {
            data: { id: 'aplicaciones-internet-backend', source: 'aplicaciones-con-tecnologias-internet', target: 'desarrollador-backend' }
        },
        {
            data: { id: 'aplicaciones-internet-frontend', source: 'aplicaciones-con-tecnologias-internet', target: 'desarrollador-frontend' }
        },
        {
            data: { id: 'inteligencia-artificial-analista', source: 'inteligencia-artificial', target: 'analista-de-datos' }
        },
        {
            data: { id: 'inteligencia-artificial-', source: 'inteligencia-artificial', target: 'ai-data-trainer' }
        },
    ],
})

const makeTippy = (ele, nodeData) => {
    const ref = ele.popperRef();

    // Since tippy constructor requires DOM element/elements, create a placeholder
    const dummyDomEle = document.createElement('div');

    let tip = tippy( dummyDomEle, {
        getReferenceClientRect: ref.getBoundingClientRect,
        trigger: 'manual', // mandatory
        // allowHTML: true,
        // dom element inside the tippy:
        content: function(){ // function can be better for performance

            const template = document.querySelector("#tippy-content") as HTMLTemplateElement | null

            if(!template){
                console.error("tippy template element not found")
            }

            const contentEl = template?.content.cloneNode(true) as DocumentFragment
            const img = contentEl.querySelector("#img")
            const description = contentEl.querySelector("#description")
            const detailAnchor = contentEl.querySelector("#detail-anchor")

            img?.setAttribute("src", `https://upload.wikimedia.org/wikipedia/commons/a/a4/JavaScript_code.png`)
            description.innerHTML = nodeData.description
            detailAnchor?.setAttribute("href", `https://en.wikipedia.org/wiki/JavaScript`)

            return contentEl;
        },

        // your own preferences:
        arrow: true,
        placement: 'bottom',
        hideOnClick: true,

        // if interactive:
        interactive: true,
        appendTo: document.body, // or append dummyDomEle to document.body
        theme: 'light',
    } );

    return tip;
};
// Get the path of a node, when clicking on it
cy.on('click', 'node', (evt)=>{
    let node = evt.target;
    // Set styles
    node.style('border-color', 'red');

    const _node = cy.getElementById(node.id());
    const tip = makeTippy(_node, node.data());
    tip.show()
    let path = [];

    // Traverse the edges from the clicked node to the root
    while (node != null) {
        path.unshift(node.data().name);
        let parent = node.incomers().nodes().first();
        node = parent.length ? parent : null;
    }

    console.log('Path length:', path.join(' -> '));

    // Update alpine store with new data
    Alpine.store('graph').set_path(path);
})

cy.on('unselect', 'node', (evt)=>{
    let node = evt.target;

    const _node = cy.getElementById(node.id());
    const tip = makeTippy(_node, node.data().name);
    tip.hide()
    node.style('border-color', 'black');
})
