/** https://docs.djangoproject.com/en/stable/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false*/
export function getCookie(name: string) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/** Acquires the 'csrftoken' token if CSRF_USE_SESSIONS and CSRF_COOKIE_HTTPONLY are False */
export function getCSRFToken(){
    const csrftoken = getCookie('csrftoken')
    return csrftoken
}

export function formDataToURLSearchParams(formData: FormData): URLSearchParams {
    const searchParams = new URLSearchParams()
    for (const pair of formData.entries()) {
        searchParams.append(pair[0], pair[1])
    }
    return searchParams
}
/**
 * Converts a FormData object to a query string
 */
export function formDataToQueryParam(formData: FormData): string {
    const params = formDataToURLSearchParams(formData)
    return params.toString();
}
