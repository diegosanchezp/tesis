import { initHTMXutils } from 'js/utils/htmx'
import { initMentoshipPagination } from 'js/mentorship/mentorship_requests'
import { myAlpineComponent, startAlpine} from "js/utils/alpine"

startAlpine({
    components: [
    ],
    stores: [
    ]
})

// Add the event listeners for the pagination in the mentorship requests table
initMentoshipPagination()

// Init events listeners for RPC communication beteween the server and the browser
initHTMXutils()

