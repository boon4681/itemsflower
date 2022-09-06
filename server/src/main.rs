use rocket::{fs::{relative}, catchers};
use rocket::{catch, Request};

mod manual {
    use std::path::{PathBuf, Path};
    use rocket::{fs::NamedFile};
    #[rocket::get("/<version>/<path..>")]
    pub async fn colors(version: PathBuf,path: PathBuf) -> Option<NamedFile> {
        let path = Path::new(super::relative!("../source")).join(version).join("parsed").join(path);
        NamedFile::open(path).await.ok()
    }
}

#[catch(404)]
fn not_found(req: &Request) -> String {
    format!("I couldn't find '{}'. Try something else?", req.uri())
}

#[rocket::launch]
fn rocket() -> _ {
    rocket::build()
        .register("/",catchers![not_found])
        .mount("/flower/colors/", rocket::routes![manual::colors])
}