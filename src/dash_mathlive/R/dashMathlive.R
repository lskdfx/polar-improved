# AUTO GENERATED FILE - DO NOT EDIT

#' @export
dashMathlive <- function(id=NULL, value=NULL) {
    
    props <- list(id=id, value=value)
    if (length(props) > 0) {
        props <- props[!vapply(props, is.null, logical(1))]
    }
    component <- list(
        props = props,
        type = 'dash_mathlive',
        namespace = 'dash_mathlive',
        propNames = c('id', 'value'),
        package = 'dashMathlive'
        )

    structure(component, class = c('dash_component', 'list'))
}
