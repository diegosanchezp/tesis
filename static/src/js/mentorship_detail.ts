import 'flowbite';
import { initMentoshipPagination } from 'js/mentorship/mentorship_requests'
import { initHTMXutils } from 'js/utils/htmx'

initMentoshipPagination()

// Init events listeners for RPC communication beteween the server and the browser
initHTMXutils()
