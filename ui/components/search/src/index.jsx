// Island entry point. Installs `window.BERILSearch.mount(root, props)`, the
// contract the Jinja page (templates/search.html) calls after dynamically
// importing the built bundle. Mirrors the chat island's window.BERIL<Name> shape.
import { createRoot } from "react-dom/client";
import { SearchApp } from "./SearchApp.jsx";

window.BERILSearch = {
  mount(root, props) {
    createRoot(root).render(<SearchApp {...props} />);
  },
};
