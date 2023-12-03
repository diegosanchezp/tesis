export const base = "/register"
export const registerUrls = {
    complete_profile: (carreer: string, profile: string, no_spec: boolean = false) => {
        const params = new URLSearchParams("")
        params.append("carreer", carreer)
        params.append("profile", profile)
        if (no_spec) params.append("no_spec", "")
        return `/register/complete_profile?${params.toString()}`
    },
    select_specialization: (carreer: string) => {
        return `/register/select_carreer_specialization/${carreer}`
    },
    select_themes: (carreer: string) => {
        return `/register/select_themes/${carreer}`
    },
    add_exp: `${base}/add_exp`
}
