import React, { Component } from "react";

class Product extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    async componentDidMount() {
        console.log(this.props.match.params.id)
    }

    render() {
        return <h2>Product #{this.props.match.params.id}</h2>;
    }
}

export default Product