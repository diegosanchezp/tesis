import { myAlpineStore } from "js/utils/alpine"

/** Global store for instance comunication */
const profileStoreObj = {
    profile: "",
    url: "",
    change(prfl: string){
        this.profile = prfl
    },
    set_url(url: string){
        this.url = url
    }
}

export const profileStore: myAlpineStore = {
    name: "profile",
    store: profileStoreObj
}
