import { Component } from "react";
import Context from "../utils/context";
import { Link, useFetcher } from "react-router-dom";
import * as Sentry from "@sentry/react";
import { connect } from "react-redux";
import { determineBackendUrl } from "../utils/backendrouter";
class NPlusOneItem extends Component {
  async componentDidMount() {
    console.log("Mounting NPlusOneItem");
    const response = await fetch(this.props.backend + "/product/0/info?id=" + this.props.index);
    console.log({ response });
    const json = await response.json();
    console.log({ json });
    this.setState({
      data: json,
    });
  }
  render() {
    return <li>{this.props.index}</li>;
  }
}
class Nplusone extends Component {
  constructor(props) {
    super(props);
    const ids = new Array(20).fill(0).map((item, index) => index);
    this.state = {
      ids,
    };
  }
  async componentDidMount() {
    console.log("Mounting NPlusOne with props", this.props);
  }
  render() {
    return (
      <div>
        <h1>API N+1 Performance Issue</h1>
        {this.state.ids.map((index) => (
          <NPlusOneItem key={index} index={index} backend={this.props.backend} />
        ))}
        <h3>
          look at the query{" "}
          <a
            href="https://testorg-az.sentry.io/issues/?project=5808623&query=is%3Aunresolved+issue.type%3Aperformance_n_plus_one_api_calls&referrer=issue-list&statsPeriod=14d"
            rel="noreferrer"
          >
            here
          </a>
        </h3>
      </div>
    );
  }
}
export default Nplusone;