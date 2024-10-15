import { reAttachPagination as attachTablePagination } from "js/mentorship/mentorship_requests"

import htmx from 'htmx.org';
import { formDataToQueryParam } from ".";


/**
* Gets the table element given and id
*/
function getTable(table_id: string) {
    const table = document.getElementById(table_id) as HTMLTableElement

    // We don't want to continue executing code if the table doesn't exists
    if(!table){
        throw new Error(`Table id ${table_id} with not found`)
    }

    return table
}

/**
* Event listener for when whe want to change page, execute this function
* Also handles filters for the table if they exist
*/
function changeTablePage(table_id: string, table: HTMLTableElement){

    /**
    * @param evt - The click event
    */
    return (evt: MouseEvent) => {
        // Prevent a full page reload
        evt.preventDefault()

        // Get the pagination query params
        const anchor = evt.target as HTMLAnchorElement
        const paginationURL: string | null = anchor.getAttribute("href") 
        if(!paginationURL){console.log('not executing pagination, because href attribute is not defined on anchor'); return}

        // Parse table filters, if they exist
        const table_filters = table.querySelector(".table_filters")
        let filterQueryParams = ''
        if(table_filters){
            const formData = new FormData(table_filters as HTMLFormElement)
            filterQueryParams = formDataToQueryParam(formData);
        }

        // Build the final queryparam string
        const reqURL = `${paginationURL}${filterQueryParams}`

        // Make a request to get the new page
        htmx.ajax("GET",reqURL, {
            target: `#${table_id}`,
            swap: "outerHTML"
        })
    }
}

export const paginationContainerId = "pagination_container"

/**
 * Attaches the pagination event listener after the table is firstly rendered or re-rendered
 */
function attachTablePagination(table_id:string){
    
    const table = getTable(table_id)

    const tablePaginationContainer = table.querySelector(".pagination_container")
    if(!tablePaginationContainer){console.error(`Pagination Container not found for table with id ${table_id}`);return}

    tablePaginationContainer.addEventListener('click', changeTablePage(table_id, table))
}

/**
* Bootstraps the pagination for a table
* @param table_id The unique identifier of the table in the DOM
*/
export function initTablePagination(table_id: string){
    // If we are re-rendereding the table, after filtering by page or form filters,
    // re-attach the pagination event listeners
    document.body.addEventListener('htmx:afterSwap', function(event) {
        if(event.detail.elt.id === table_id){

            // Restore back the event listener
            attachTablePagination(table_id)
        }
    });

    document.addEventListener("reAttachPagination", () => {
        console.log('reAttachPagination')
        attachTablePagination(table_id)
    })

    document.addEventListener("DOMContentLoaded", () => {
        attachTablePagination(table_id)
    })
}
