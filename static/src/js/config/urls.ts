export const registerUrls = {
    complete_profile: (carreer: string, no_spec: boolean = false) => {
        const params = new URLSearchParams("")
        params.append("carreer", carreer)
        if (no_spec) params.append("no_spec", "")
        return `/register/complete_profile?${params.toString()}`
    }
}
