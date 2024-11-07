import 'flowbite';
import { initModals } from 'flowbite';
import { initHTMXutils } from 'js/utils/htmx'
import { initTablePagination } from './utils/table'
import { initMentorReqTable } from './mentor/shared'
import { startAlpine, myAlpineComponent } from 'js/utils/alpine'
import htmx from 'htmx.org';

// Add the event listeners for the pagination in the mentorship requests table
initTablePagination("mentorship_req_table")

// Init events listeners for RPC communication beteween the server and the browser
initHTMXutils()

initMentorReqTable()

/*
* Confirmation component two clicks should be made
* before the action is executed.
*/
const DeleteMentorshipReq: myAlpineComponent = {
    name: 'deleteMentorshipComponent',
    component: (mentorshipReqPk: number, url: string) => ({
        mentorshipReqPk: mentorshipReqPk,
        confirm: false,
        sendHtmxReq(){
            if(!this.confirm){
                // set confirm to true to show the '?'
                this.confirm = true
                return
            }
            // Action
            htmx.ajax("POST",url, {
                target: "#mentorship_req_table",
                swap: "outerHTML",
            })
        }
    })

}
startAlpine({
    components: [DeleteMentorshipReq],
    stores: []
})

document.addEventListener("DOMContentLoaded", ()=>{
    document.body.addEventListener('htmx:afterSwap', function(event) {
        // Re-attach flowbite event listeners for 'Eliminar' btn only if we
        // are showing the reading state of a mentorship 
        const editElement = event.detail.elt.querySelector('#mentorship-form')
        const isFromEdit = Boolean(editElement)
        if(event.detail.elt.id === 'mentorship-info' && !isFromEdit){
            initModals()
        }
    });
})


