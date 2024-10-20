import { initHTMXutils } from 'js/utils/htmx'
import { startAlpine } from "js/utils/alpine"
import { initTablePagination } from './utils/table'
import { initMentorReqTable } from './mentor/shared'
startAlpine({
    components: [
    ],
    stores: [
    ]
})

// Add the event listeners for the pagination in the mentorship requests table
initTablePagination("mentorship_req_table")

// Init events listeners for RPC communication beteween the server and the browser
initHTMXutils()

initMentorReqTable()
