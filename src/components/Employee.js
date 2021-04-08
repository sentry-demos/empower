import React, { Component } from "react";

class Employee extends Component {
    constructor(props) {
        super(props);
        this.state = {};
    }

    async componentDidMount() {
        console.log(this.props.match.params.name)
    }

    render() {
        return <h2>Employee {this.props.match.params.name}</h2>;
    }
}

export default Employee