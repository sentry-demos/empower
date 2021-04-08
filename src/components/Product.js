import React, { Component } from "react";

class Product extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    // could use the product ID from this.props to look up the product info on the back-end
    // product info could be an image, text, reviews. not required.
    async componentDidMount() {
        console.log("componentDidMount.this.props", this.props)
    }

    render() {
        return <h2>Product #{this.props.match.params.id}</h2>;
    }
}

export default Product