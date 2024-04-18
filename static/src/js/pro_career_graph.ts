import {startAlpine} from 'js/utils/alpine';
import cytoscape from 'cytoscape';
// import elk from 'cytoscape-elk';
import cola from 'cytoscape-cola';
import tippy from 'tippy.js';
import 'tippy.js/dist/tippy.css';

const blueColor = '#006090'
const yellowColor = '#ffd200'

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
cytoscape.use( cola );

const graph_data = JSON.parse(document.getElementById('graph_data').textContent)
console.log(graph_data)

const cy = cytoscape({
    // container to render in
    container: document.getElementById('cy'),
    // For 'single' the previous elements are unselected
    selectionType: 'single',
    // https://github.com/cytoscape/cytoscape.js-elk
    layout: {
        name: 'cola',
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
                "font-size": "7px",
                "text-max-width": "100px",
                'height': '30',
                "text-wrap": "wrap",
                // This puts the text inside the node
                'text-valign': 'center',
                'text-halign': 'center',
            }
        },
        {
            selector: 'node[NodeType = "AcademicCareer"]',
            style: {
                'border-color': blueColor, // blue color
                'border-width': 2,
            }
        },
        {
            selector: 'node[NodeType = "ProfessionalCareer"]',
            style: {
                'border-color': yellowColor, // yellow color
                'border-width': 1,
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
        },

    ],
    elements: graph_data,
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
            const title = contentEl.querySelector("#title")
            const description = contentEl.querySelector("#description")
            const detailAnchor = contentEl.querySelector("#detail-anchor")


            // If there is no image, replace it with a placeholder
            if(nodeData.NodeType === "ProfessionalCareer"){
                if (!nodeData.imgURL || nodeData.imgURL === ""){
                    const template = document.querySelector("#no-img") as HTMLTemplateElement | null
                    const imgPlaceHolderEl = template?.content.cloneNode(true) as DocumentFragment
                    img?.replaceWith(imgPlaceHolderEl)
                } else {
                    img?.setAttribute("src", nodeData.imgURL)
                }
            }


            title.innerHTML = nodeData.name
            description.innerHTML = nodeData.description
            detailAnchor?.setAttribute("href", nodeData.career_url)

            if(["AcademicCareer", "CareerSpec"].includes(nodeData.NodeType)){
                img?.remove()
                detailAnchor?.remove()
            }
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
    let selectedNode = evt.target;
    // Set styles
    selectedNode.style('border-color', 'red');

    const _node = cy.getElementById(selectedNode.id());
    const node_data = selectedNode.data();
    const tip = makeTippy(_node, selectedNode.data());
    tip.show()
    let path = [];

    // Traverse the edges from the clicked node to the root
    while (selectedNode != null) {
        // Add to the array
        path.unshift(selectedNode.data().name);
        let parent = selectedNode.incomers().nodes().first();
        parent.style('border-color', 'red');
        // Style the edge
        selectedNode.incomers().style(
            {'line-color': 'red', 'target-arrow-color': 'red'}
        );
        selectedNode = parent.length ? parent : null;
    }

    console.log('Path length:', path.join(' -> '));

    // Update alpine store with new data
    Alpine.store('graph').set_path(path);
})

cy.on('unselect', 'node', (evt)=>{
    let selectedNode = evt.target;

    const _node = cy.getElementById(selectedNode.id());
    const tip = makeTippy(_node, selectedNode.data().name);
    tip.hide()
    selectedNode.removeStyle();

    // Traverse the edges from the clicked node to the root
    while (selectedNode != null) {
        let parent = selectedNode.incomers().nodes().first();
        parent.removeStyle();
        // Remove applied style of incoming edges
        selectedNode.incomers().removeStyle();
        selectedNode = parent.length ? parent : null;
    }
})
